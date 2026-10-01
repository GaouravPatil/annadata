"""Live mandi prices from api.data.gov.in (Govt. of India OGD platform).

Resource: 9ef84268-d588-465a-a308-a864a43d0070
Fields: state, district, market, commodity, variety, grade,
        arrival_date, min_price, max_price, modal_price
"""
import httpx
import os
import logging

logger = logging.getLogger(__name__)

MANDI_RESOURCE = "9ef84268-d588-465a-a308-a864a43d0070"
MANDI_URL = f"https://api.data.gov.in/resource/{MANDI_RESOURCE}"

# Common aliases / spellings -> canonical data.gov.in state names
STATE_ALIASES = {
    "maharashtra": "Maharashtra",
    "gujarat": "Gujarat",
    "punjab": "Punjab",
    "haryana": "Haryana",
    "uttar pradesh": "Uttar Pradesh",
    "up": "Uttar Pradesh",
    "madhya pradesh": "Madhya Pradesh",
    "mp": "Madhya Pradesh",
    "rajasthan": "Rajasthan",
    "karnataka": "Karnataka",
    "tamil nadu": "Tamil Nadu",
    "tamilnadu": "Tamil Nadu",
    "telangana": "Telangana",
    "andhra pradesh": "Andhra Pradesh",
    "bihar": "Bihar",
    "west bengal": "West Bengal",
    "odisha": "Odisha",
    "orissa": "Odisha",
    "kerala": "Kerala",
    "keralam": "Kerala",
    "chhattisgarh": "Chattisgarh",
    "assam": "Assam",
    "jharkhand": "Jharkhand",
    "himachal pradesh": "Himachal Pradesh",
    "uttarakhand": "Uttarakhand",
    "goa": "Goa",
    "delhi": "NCT of Delhi",
    "nct of delhi": "NCT of Delhi",
}

COMMODITY_ALIASES = {
    "wheat": "Wheat",
    "rice": "Rice",
    "paddy": "Paddy",
    "onion": "Onion",
    "tomato": "Tomato",
    "cotton": "Cotton",
    "sugarcane": "Sugarcane",
    "soybean": "Soyabean",
    "soyabean": "Soyabean",
    "soya": "Soyabean",
    "maize": "Maize",
    "potato": "Potato",
    "mustard": "Mustard",
    "groundnut": "Groundnut",
    "sunflower": "Sunflower",
    "bajra": "Bajra",
    "jowar": "Jowar",
    "barley": "Barley",
    "gram": "Gram",
    "tur": "Tur",
    "moong": "Moong",
    "urad": "Urad",
}


def normalise_state(raw: str | None) -> str | None:
    if not raw:
        return None
    key = raw.strip().lower()
    return STATE_ALIASES.get(key, raw.strip().title())


def normalise_commodity(raw: str | None) -> str | None:
    if not raw or raw.lower() == "all":
        return None
    key = raw.strip().lower()
    return COMMODITY_ALIASES.get(key, raw.strip().title())


def parse_location(location: str | None) -> dict:
    """Infer {state, district} from a free-text farmer location.

    e.g. 'Nashik, Maharashtra' -> {district: 'Nashik', state: 'Maharashtra'}
         'Ludhiana, Punjab'    -> {district: 'Ludhiana', state: 'Punjab'}
         'Maharashtra'         -> {district: None, state: 'Maharashtra'}
    """
    if not location:
        return {"state": "Maharashtra", "district": None}
    parts = [p.strip() for p in location.split(",") if p.strip()]
    if len(parts) >= 2:
        district, state_raw = parts[0], parts[-1]
        return {"state": normalise_state(state_raw) or "Maharashtra", "district": district}
    single = parts[0] if parts else ""
    state = normalise_state(single)
    # If single token matches a known state keep it as state, else treat as district in Maharashtra
    if single.strip().lower() in STATE_ALIASES:
        return {"state": state, "district": None}
    # Heuristic: well-known state names title-cased; otherwise district
    known_states = set(STATE_ALIASES.values())
    if state in known_states:
        return {"state": state, "district": None}
    return {"state": "Maharashtra", "district": single or None}


async def fetch_mandi_prices(
    state: str | None = None,
    district: str | None = None,
    commodity: str | None = None,
    market: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict:
    """Fetch live mandi records. Falls back from district -> state level on empty."""
    api_key = os.getenv(
        "DATA_GOV_API_KEY",
        "579b464db66ec23bdd000001cdd3946e44ce4aad38534209a181d0",
    )
    state = normalise_state(state) if state else None
    commodity_norm = normalise_commodity(commodity)

    def build_params(use_district: bool) -> dict:
        params = {"api-key": api_key, "format": "json", "limit": min(max(limit, 1), 100), "offset": offset}
        if state:
            params["filters[state]"] = state
        if use_district and district:
            params["filters[district]"] = district
        if commodity_norm:
            params["filters[commodity]"] = commodity_norm
        if market:
            params["filters[market]"] = market
        return params

    async with httpx.AsyncClient() as client:
        # 1) try with district filter
        try:
            resp = await client.get(MANDI_URL, params=build_params(True), timeout=15)
            data = resp.json()
        except Exception as e:
            logger.warning("Mandi API error: %s", e)
            return {"records": [], "error": f"Mandi API unavailable: {e}", "state": state, "district": district}

        records = data.get("records") or []
        fallback_used = False
        # 2) fallback to state-only when district yields nothing
        if not records and district:
            try:
                resp2 = await client.get(MANDI_URL, params=build_params(False), timeout=15)
                data2 = resp2.json()
                records = data2.get("records") or []
                fallback_used = True if records else False
            except Exception as e:
                logger.warning("Mandi fallback error: %s", e)

        return {
            "records": records,
            "total": data.get("total"),
            "count": len(records),
            "state": state,
            "district": None if fallback_used else district,
            "fallback_to_state": fallback_used,
            "commodity": commodity_norm or commodity,
        }


async def fetch_mandi_for_location(location: str | None, commodity: str | None = None, limit: int = 20) -> dict:
    """Convenience: parse farmer location string then fetch prices."""
    parsed = parse_location(location)
    result = await fetch_mandi_prices(
        state=parsed["state"],
        district=parsed["district"],
        commodity=commodity,
        limit=limit,
    )
    result["farmer_location"] = location
    return result
