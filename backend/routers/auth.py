from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from pydantic import BaseModel
from models.database import Farmer, get_db
from jose import jwt
import uuid, os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret")

class RegisterRequest(BaseModel):
    name: str
    phone: str = ""
    language: str = "en"
    location: str = ""
    age: int | None = None

@router.post("/register")
def register(req: RegisterRequest, db: DBSession = Depends(get_db)):

    if req.phone:
        existing = db.query(Farmer).filter(Farmer.phone == req.phone).first()
        if existing:
            token = jwt.encode({"farmer_id": existing.id}, SECRET_KEY, algorithm="HS256")
            return {"token": token, "farmer_id": existing.id}

    farmer = Farmer(
        id=str(uuid.uuid4()),
        name=req.name,
        phone=str(uuid.uuid4()), 
        language=req.language,
        location=req.location,
        age=req.age
    )
    db.add(farmer)
    db.commit()
    token = jwt.encode({"farmer_id": farmer.id}, SECRET_KEY, algorithm="HS256")
    return {"token": token, "farmer_id": farmer.id}