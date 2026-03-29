import httpx

async def get_weather(lat: float, lon: float):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "precipitation_sum,temperature_2m_max,temperature_2m_min",
        "forecast_days": 7,
        "timezone": "Asia/Kolkata"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()

    forecast = []
    days = data["daily"]
    for i in range(7):
        forecast.append({
            "date": days["time"][i],
            "max_temp": days["temperature_2m_max"][i],
            "min_temp": days["temperature_2m_min"][i],
            "rainfall_mm": days["precipitation_sum"][i]
        })
    return forecast