"""Public + authenticated info endpoints: profile, weather, mandi prices."""
from fastapi import APIRouter, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from fastapi import HTTPException
from sqlalchemy.orm import Session as DBSession
from models.database import Farmer, get_db
from services.weather import get_weather_full, get_weather_for_location
from services.geocode import geocode_location
from services.mandi import fetch_mandi_prices, fetch_mandi_for_location, parse_location
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
bearer = HTTPBearer(auto_error=False)
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret")


def _optional_farmer_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> Optional[str]:
    if not credentials:
        return None
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload.get("farmer_id")
    except JWTError:
        return None


def _require_farmer_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> str:
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing token")
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        farmer_id = payload.get("farmer_id")
        if not farmer_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return farmer_id
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")


@router.get("/me")
def me(db: DBSession = Depends(get_db), farmer_id: str = Depends(_require_farmer_id)):
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(status_code=401, detail="Farmer not found")
    return {
        "farmer_id": farmer.id,
        "name": farmer.name,
        "location": farmer.location,
        "language": farmer.language,
        "age": farmer.age,
    }


@router.get("/weather")
async def weather(
    location: Optional[str] = Query(default=None, description="e.g. 'Nashik, Maharashtra'"),
    lat: Optional[float] = Query(default=None),
    lon: Optional[float] = Query(default=None),
):
    """Realtime weather. Prefer explicit lat/lon, else geocode `location` string."""
    try:
        if lat is not None and lon is not None:
            full = await get_weather_full(lat, lon)
            full["requested_location"] = location
            return full
        if location:
            return await get_weather_for_location(location)
        raise HTTPException(status_code=400, detail="Provide ?location= or ?lat=&lon=")
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Weather unavailable: {e}")


@router.get("/geocode")
async def geocode(q: str = Query(..., description="Place name to geocode")):
    geo = await geocode_location(q)
    if not geo:
        raise HTTPException(status_code=404, detail=f"Could not locate '{q}'")
    return geo


@router.get("/mandi-prices")
async def mandi_prices(
    location: Optional[str] = Query(default=None, description="Farmer location, e.g. 'Nashik, Maharashtra'"),
    state: Optional[str] = Query(default=None),
    district: Optional[str] = Query(default=None),
    commodity: Optional[str] = Query(default=None),
    market: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """Live mandi prices. If `location` is given, state/district are inferred from it."""
    try:
        if location and not (state or district):
            return await fetch_mandi_for_location(location, commodity=commodity, limit=limit)
        parsed = parse_location(location) if location else {"state": None, "district": None}
        eff_state = state or parsed.get("state") or "Maharashtra"
        eff_district = district if district is not None else parsed.get("district")
        result = await fetch_mandi_prices(
            state=eff_state, district=eff_district, commodity=commodity,
            market=market, limit=limit, offset=offset,
        )
        result["farmer_location"] = location
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Mandi prices unavailable: {e}")


@router.get("/mandi-prices/me")
async def mandi_prices_for_me(
    commodity: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: DBSession = Depends(get_db),
    farmer_id: str = Depends(_require_farmer_id),
):
    """Mandi prices scoped to the logged-in farmer's stored location."""
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(status_code=401, detail="Farmer not found")
    try:
        return await fetch_mandi_for_location(farmer.location, commodity=commodity, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Mandi prices unavailable: {e}")
