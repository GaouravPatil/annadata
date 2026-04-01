from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from pydantic import BaseModel
from models.database import Message, Session as ChatSession, get_db
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.agent import get_ai_response
import uuid, os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
bearer = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret")

def get_farmer_id(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload["farmer_id"]
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Invalid token")

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    latitude: float | None = None
    longitude: float | None = None

@router.post("/chat")
async def chat(req: ChatRequest, db: DBSession = Depends(get_db),
               farmer_id: str = Depends(get_farmer_id)):

    session_id = req.session_id
    if not session_id or session_id == "null":
        session = ChatSession(id=str(uuid.uuid4()), farmer_id=farmer_id)
        db.add(session)
        db.commit()
        session_id = session.id

    user_msg = Message(
        id=str(uuid.uuid4()),
        session_id=session_id,
        role="user",
        content=req.message,
        created_at=datetime.utcnow()
    )
    db.add(user_msg)
    db.commit()

    reply = await get_ai_response(
        message=req.message,
        lat=req.latitude,
        lon=req.longitude
    )

    ai_msg = Message(
        id=str(uuid.uuid4()),
        session_id=session_id,
        role="assistant",
        content=reply,
        created_at=datetime.utcnow()
    )
    db.add(ai_msg)
    db.commit()

    return {"reply": reply, "session_id": session_id}

@router.get("/history/{session_id}")
def history(session_id: str, db: DBSession = Depends(get_db),
            farmer_id: str = Depends(get_farmer_id)):
    messages = db.query(Message).filter(
        Message.session_id == session_id
    ).order_by(Message.created_at).all()
    return [{"role": m.role, "content": m.content} for m in messages]
