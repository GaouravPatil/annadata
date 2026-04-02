import httpx
import os
from services.weather import get_weather
from services.cache import get_session_history, add_to_session
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

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

        if lat and lon:
            context_parts.append(f"Farmer location: latitude={lat}, longitude={lon} (Maharashtra, India region)")

        context = "\n\n".join(context_parts) if context_parts else ""

        # build messages with history
        messages = [
            {
                "role": "system",
                "content": f"""You are AnnaData, an AI agricultural assistant for Indian farmers.
Help farmers with crop advice, weather insights, market prices and farming guidance.
Always respond in the same language the farmer uses (Hindi, Marathi, or English).
Keep responses clear, practical and actionable. Avoid technical jargon.
Be encouraging and respectful. Give specific actionable advice.
{f'Real-time data available:{chr(10)}{context}' if context else ''}"""
            }
        ]

        # add conversation history (last 6 messages only to save tokens)
        if session_id:
            history = get_session_history(session_id)
            for msg in history[-6:]:
                messages.append(msg)

        # add current message
        messages.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=1024
        )

        reply = response.choices[0].message.content

        # save to cache
        if session_id:
            add_to_session(session_id, "user", message)
            add_to_session(session_id, "assistant", reply)

        return reply

    except Exception as e:
        return f"Sorry, I could not process your request right now. ({str(e)})"
