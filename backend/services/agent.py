import httpx
import os
import logging
from services.weather import get_weather
from services.cache import get_session_history, add_to_session
from services.rag import search_knowledge_base
from dotenv import load_dotenv
from mistralai.client import Mistral

load_dotenv()

logger = logging.getLogger(__name__)

# Mistral chat model. Override with MISTRAL_MODEL env if needed.
# NOTE: on free / rate-limited keys, mistral-small/medium-LATEST often 429s.
# ministral-8b-latest / ministral-14b-latest are much more permissive.
# Good defaults for this app (multilingual EN/HI/MR, cheap, fast):
# - ministral-8b-latest (recommended default, verified working on limited keys)
# - ministral-14b-latest (better quality, also permissive)
# - mistral-small-latest -> Mistral Small 4 (use when quota allows)
# - mistral-medium-latest -> Mistral Medium 3.5 (use when quota allows)
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "ministral-8b-latest")
MISTRAL_FALLBACK_MODEL = os.getenv("MISTRAL_FALLBACK_MODEL", "ministral-14b-latest")


def get_mistral_client() -> Mistral:
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise RuntimeError(
            "MISTRAL_API_KEY is not set. Please set it in your backend/.env file."
        )
    return Mistral(api_key=api_key)


def _extract_reply_text(response) -> str:
    """Handle Mistral content being str or list[ContentChunk]."""
    content = response.choices[0].message.content
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    # list of chunks: [{"type": "text", "text": "..."}, ...] or objects
    parts = []
    for chunk in content:
        if isinstance(chunk, str):
            parts.append(chunk)
        elif isinstance(chunk, dict):
            parts.append(chunk.get("text", ""))
        else:
            parts.append(getattr(chunk, "text", "") or "")
    return "".join(parts)


async def get_weather_context(lat: float, lon: float) -> str:
    try:
        forecast = await get_weather(lat, lon)
        result = "7-day weather forecast:\n"
        for day in forecast:
            result += f"{day['date']}: Max {day['max_temp']}C, Min {day['min_temp']}C, Rainfall {day['rainfall_mm']}mm\n"
        return result
    except Exception as e:
        return f"Weather data unavailable: {str(e)}"

async def get_mandi_prices(crop: str, state: str = "Maharashtra") -> str:
    try:
        url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
        params = {
            "api-key": os.getenv("DATA_GOV_API_KEY", "579b464db66ec23bdd000001cdd3946e44ce4aad38534209a181d0"),
            "format": "json",
            "filters[commodity]": crop,
            "filters[state]": state,
            "limit": 5
        }
        async with httpx.AsyncClient() as client_http:
            response = await client_http.get(url, params=params, timeout=10)
            data = response.json()

        if not data.get("records"):
            return f"No mandi price data found for {crop} in {state}."

        result = f"Current mandi prices for {crop} in {state}:\n"
        for record in data["records"]:
            result += f"Market: {record.get('market', 'N/A')}, "
            result += f"Min: Rs.{record.get('min_price', 'N/A')}, "
            result += f"Max: Rs.{record.get('max_price', 'N/A')}, "
            result += f"Modal: Rs.{record.get('modal_price', 'N/A')}\n"
        return result
    except Exception as e:
        return f"Mandi price data unavailable: {str(e)}"

def detect_query_type(message: str) -> dict:
    message_lower = message.lower()
    return {
        "needs_weather": any(w in message_lower for w in ["weather", "rain", "temperature", "forecast", "irrigation", "water", "मौसम", "बारिश"]),
        "needs_price": any(w in message_lower for w in ["price", "market", "mandi", "sell", "rate", "cost", "भाव", "मंडी"]),
        "needs_rag": any(w in message_lower for w in ["scheme", "government", "pm-kisan", "pmfby", "insurance", "subsidy", "storage", "pest", "disease", "fertilizer", "how to grow", "cultivat", "harvest", "helpline", "yojana", "किसान", "योजना", "कीट", "बीमा"]),
        "crop_mentioned": next((w for w in ["wheat", "rice", "onion", "tomato", "cotton", "sugarcane", "soybean", "maize", "गेहूं", "चावल", "प्याज"] if w in message_lower), None)
    }

async def get_ai_response(message: str, lat: float = None, lon: float = None, language: str = "en", session_id: str = None) -> str:
    try:
        query_info = detect_query_type(message)
        context_parts = []

        if query_info["needs_weather"] and lat and lon:
            weather_data = await get_weather_context(lat, lon)
            context_parts.append(weather_data)

        if query_info["needs_price"] and query_info["crop_mentioned"]:
            price_data = await get_mandi_prices(query_info["crop_mentioned"])
            context_parts.append(price_data)

        if query_info["needs_rag"] or query_info["crop_mentioned"]:
            rag_data = search_knowledge_base(message)
            context_parts.append(rag_data)

        if lat and lon:
            context_parts.append(f"Farmer location: latitude={lat}, longitude={lon} (Maharashtra, India region)")

        context = "\n\n".join(context_parts) if context_parts else ""

        messages = [
            {
                "role": "system",
                "content": f"""You are AnnaData, an AI agricultural assistant for Indian farmers.
Help farmers with crop advice, weather insights, market prices and farming guidance.
Always respond in the same language the farmer uses (Hindi, Marathi, or English).
Keep responses clear, practical and actionable. Avoid technical jargon.
Be encouraging and respectful. Give specific actionable advice.
{f'Real-time data and knowledge available:{chr(10)}{context}' if context else ''}"""
            }
        ]

        if session_id:
            history = get_session_history(session_id)
            for msg in history[-6:]:
                # cache stores {"role": "user"|"assistant", "content": str}
                # Mistral accepts same shape
                if msg.get("role") in ("user", "assistant", "system", "tool") and isinstance(msg.get("content"), str):
                    messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": message})

        mistral_client = get_mistral_client()
        # Use async API to avoid blocking the FastAPI event loop.
        # Retry once on rate-limit with fallback model.
        try:
            response = await mistral_client.chat.complete_async(
                model=MISTRAL_MODEL,
                messages=messages,
                max_tokens=1024,
            )
        except Exception as e:
            err = str(e)
            if ("429" in err or "rate" in err.lower()) and MISTRAL_FALLBACK_MODEL != MISTRAL_MODEL:
                logger.warning("Primary model %s rate-limited, trying fallback %s", MISTRAL_MODEL, MISTRAL_FALLBACK_MODEL)
                response = await mistral_client.chat.complete_async(
                    model=MISTRAL_FALLBACK_MODEL,
                    messages=messages,
                    max_tokens=1024,
                )
            else:
                raise

        reply = _extract_reply_text(response)

        if session_id:
            add_to_session(session_id, "user", message)
            add_to_session(session_id, "assistant", reply)

        return reply

    except Exception as e:
        logger.exception("Mistral chat failed (model=%s): %s", MISTRAL_MODEL, e)
        return f"Sorry, I could not process your request right now. ({str(e)})"
