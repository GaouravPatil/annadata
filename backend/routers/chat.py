from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from pydantic import BaseModel
from models.database import Message, Session as ChatSession, Farmer, get_db
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.agent import get_ai_response
from services.cache import get_session_history, add_to_session
import uuid, os
from datetime import datetime
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

router = APIRouter()
bearer = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret")


def get_farmer_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> str:
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        farmer_id = payload.get("farmer_id")
        if not farmer_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return farmer_id
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@router.post("/chat")
async def chat(
    req: ChatRequest,
    db: DBSession = Depends(get_db),
    farmer_id: str = Depends(get_farmer_id)
):
    # verify farmer exists
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(status_code=401, detail="Farmer not found")

    # create or use existing session
    session_id = req.session_id
    if not session_id or session_id == "null" or session_id == "undefined":
        session = ChatSession(
            id=str(uuid.uuid4()),
            farmer_id=farmer_id
        )
        db.add(session)
        db.commit()
        session_id = session.id

    # verify session belongs to this farmer
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.farmer_id == farmer_id
    ).first()
    if not session:
        raise HTTPException(status_code=403, detail="Session not found")

    # load history from DB into cache if cache is empty
    history = get_session_history(session_id)
    if not history:
        past_messages = db.query(Message).filter(
            Message.session_id == session_id
        ).order_by(Message.created_at).all()
        for m in past_messages[-10:]:
            add_to_session(session_id, m.role, m.content)

    # save user message
    user_msg = Message(
        id=str(uuid.uuid4()),
        session_id=session_id,
        role="user",
        content=req.message,
        created_at=datetime.utcnow()
    )
    db.add(user_msg)
    db.commit()

    # get AI response
    try:
        reply = await get_ai_response(
            message=req.message,
            lat=req.latitude,
            lon=req.longitude,
            session_id=session_id
        )
    except Exception as e:
        reply = f"Sorry, I could not process your request right now. Please try again."

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
def history(
    session_id: str,
    db: DBSession = Depends(get_db),
    farmer_id: str = Depends(get_farmer_id)
):
    # verify session belongs to farmer
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.farmer_id == farmer_id
    ).first()
    if not session:
        raise HTTPException(status_code=403, detail="Session not found")

    messages = db.query(Message).filter(
        Message.session_id == session_id
    ).order_by(Message.created_at).all()

    return [{"role": m.role, "content": m.content} for m in messages]


@router.get("/sessions")
def get_sessions(
    db: DBSession = Depends(get_db),
    farmer_id: str = Depends(get_farmer_id)
):
    sessions = db.query(ChatSession).filter(
        ChatSession.farmer_id == farmer_id
    ).order_by(ChatSession.created_at.desc()).all()

    result = []
    for s in sessions:
        first_msg = db.query(Message).filter(
            Message.session_id == s.id,
            Message.role == "user"
        ).order_by(Message.created_at).first()

        if first_msg:
            title = first_msg.content[:40] + "..." if len(first_msg.content) > 40 else first_msg.content
        else:
            title = "New Chat"

        result.append({
            "session_id": s.id,
            "title": title,
            "created_at": s.created_at.isoformat()
        })

    return result


@router.delete("/sessions/{session_id}")
def delete_session(
    session_id: str,
    db: DBSession = Depends(get_db),
    farmer_id: str = Depends(get_farmer_id)
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.farmer_id == farmer_id
    ).first()
    if not session:
        raise HTTPException(status_code=403, detail="Session not found")

    db.query(Message).filter(Message.session_id == session_id).delete()
    db.delete(session)
    db.commit()

    return {"status": "deleted"}
