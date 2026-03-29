from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models.database import Message, Session as ChatSession, get_db
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uuid, os
from datetime import datetime

router = APIRouter()
bearer = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret")

def get_farmer_id(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload["farmer_id"]
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    latitude: float | None = None
    longitude: float | None = None

@router.post("/chat")
def chat(req: ChatRequest, db: Session = Depends(get_db),
         farmer_id: str = Depends(get_farmer_id)):

    # create session if none provided
    session_id = req.session_id
    if not session_id:
        session = ChatSession(id=str(uuid.uuid4()), farmer_id=farmer_id)
        db.add(session)
        db.commit()
        session_id = session.id

    # save user message
    user_msg = Message(
        id=str(uuid.uuid4()),
        session_id=session_id,
        role="user",
        content=req.message,
        created_at=datetime.utcnow()
    )
    db.add(user_msg)

    # --- AI reply goes here in Day 6, for now return a stub ---
    reply = f"Hello farmer! You asked: '{req.message}'. AI agent coming soon."

    # save assistant message
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
def history(session_id: str, db: Session = Depends(get_db),
            farmer_id: str = Depends(get_farmer_id)):
    messages = db.query(Message).filter(
        Message.session_id == session_id
    ).order_by(Message.created_at).all()

    return [{"role": m.role, "content": m.content} for m in messages]