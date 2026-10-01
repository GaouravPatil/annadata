"""Geocode a free-text location (e.g. 'Nashik, Maharashtra') to lat/lon.

Uses the free Open-Meteo geocoding API — no key required.
"""
import httpx
import logging

logger = logging.getLogger(__name__)

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"


async def geocode_location(location: str) -> dict | None:
    """Return {latitude, longitude, name, state, country} or None."""
    location = (location or "").strip()
    if not location:
        return None
    # Take the most specific part first: "Nashik, Maharashtra" -> try full, then "Nashik"
    candidates = [location]
    if "," in location:
        parts = [p.strip() for p in location.split(",") if p.strip()]
        # most specific first
        candidates.extend(parts)
    async with httpx.AsyncClient() as client:
        for query in candidates:
            try:
                resp = await client.get(
                    GEOCODE_URL,
                    params={"name": query, "count": 1, "language": "en", "format": "json"},
                    timeout=10,
                )
                data = resp.json()
                results = data.get("results") or []
                if results:
                    top = results[0]
                    return {
                        "latitude": top.get("latitude"),
                        "longitude": top.get("longitude"),
                        "name": top.get("name"),
                        "state": top.get("admin1"),
                        "district": top.get("admin2"),
                        "country": top.get("country"),
                    }
            except Exception as e:
                logger.warning("Geocode failed for %r: %s", query, e)
                continue
    return None
