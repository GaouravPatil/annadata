import httpx

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Icy fog",
    51: "Light drizzle",
    53: "Drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Snow",
    75: "Heavy snow",
    80: "Slight showers",
    81: "Showers",
    82: "Violent showers",
    95: "Thunderstorm",
    96: "Thunderstorm + hail",
    99: "Thunderstorm + heavy hail",
}


def describe_code(code) -> str:
    try:
        return WEATHER_CODES.get(int(code), "—")
    except Exception:
        return "—"


async def get_weather(lat: float, lon: float):
    """7-day daily forecast (kept for backwards-compat with agent)."""
    full = await get_weather_full(lat, lon)
    return full["daily"]


async def get_weather_full(lat: float, lon: float) -> dict:
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weathercode,wind_speed_10m",
        "daily": "weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max",
        "forecast_days": 7,
        "timezone": "Asia/Kolkata",
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(FORECAST_URL, params=params, timeout=15)
        data = response.json()

    days = data.get("daily", {})
    times = days.get("time", [])
    forecast = []
    for i in range(len(times)):
        code = (days.get("weathercode") or [None] * len(times))[i]
        forecast.append({
            "date": times[i],
            "max_temp": (days.get("temperature_2m_max") or [None] * len(times))[i],
            "min_temp": (days.get("temperature_2m_min") or [None] * len(times))[i],
            "rainfall_mm": (days.get("precipitation_sum") or [0] * len(times))[i],
            "rain_chance": (days.get("precipitation_probability_max") or [None] * len(times))[i],
            "weathercode": code,
            "condition": describe_code(code),
        })

    cur = data.get("current", {}) or {}
    current = {
        "temp_c": cur.get("temperature_2m"),
        "feels_like_c": cur.get("apparent_temperature"),
        "humidity": cur.get("relative_humidity_2m"),
        "wind_kmh": cur.get("wind_speed_10m"),
        "weathercode": cur.get("weathercode"),
        "condition": describe_code(cur.get("weathercode")),
        "time": cur.get("time"),
    }
    return {"latitude": lat, "longitude": lon, "current": current, "daily": forecast}


async def get_weather_for_location(location: str) -> dict:
    """Geocode a location string then return full weather bundle."""
    from services.geocode import geocode_location

    geo = await geocode_location(location)
    if not geo or not geo.get("latitude"):
        raise ValueError(f"Could not locate '{location}'. Try 'District, State'.")
    full = await get_weather_full(geo["latitude"], geo["longitude"])
    full["resolved"] = geo
    full["requested_location"] = location
    return full
