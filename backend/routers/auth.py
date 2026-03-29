from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models.database import Farmer, get_db
from jose import jwt
from passlib.context import CryptContext
import uuid, os

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"])
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret")

class RegisterRequest(BaseModel):
    name: str
    phone: str
    language: str = "en"
    location: str = ""

@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(Farmer).filter(Farmer.phone == req.phone).first()
    if existing:
        # already registered — just return a token
        token = jwt.encode({"farmer_id": existing.id}, SECRET_KEY, algorithm="HS256")
        return {"token": token, "farmer_id": existing.id}

    farmer = Farmer(
        id=str(uuid.uuid4()),
        name=req.name,
        phone=req.phone,
        language=req.language,
        location=req.location
    )
    db.add(farmer)
    db.commit()
    token = jwt.encode({"farmer_id": farmer.id}, SECRET_KEY, algorithm="HS256")
    return {"token": token, "farmer_id": farmer.id}