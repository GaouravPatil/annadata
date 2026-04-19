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

load_dotenv()

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
async def chat(req: ChatRequest, db: DBSession = Depends(get_db),
               farmer_id: str = Depends(get_farmer_id)):
               

    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(status_code=401, detail="Farmer not found — please log in again")

    session_id = req.session_id
    if not session_id or session_id == "null":
        session = ChatSession(id=str(uuid.uuid4()), farmer_id=farmer_id)
        db.add(session)
        db.commit()
        session_id = session.id

    # load history from DB into cache if cache is empty for this session
    history = get_session_history(session_id)
    if not history:
        past_messages = db.query(Message).filter(
        Message.session_id == session_id
    ).order_by(Message.created_at).all()
        for m in past_messages[-10:]:
         add_to_session(session_id, m.role, m.content)

    # save user message to DB
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
        lon=req.longitude,
        session_id=session_id
    )

    # save assistant message to DB
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

@router.get("/sessions")
def get_sessions(db: DBSession = Depends(get_db),
                 farmer_id: str = Depends(get_farmer_id)):
    sessions = db.query(ChatSession).filter(
        ChatSession.farmer_id == farmer_id
    ).order_by(ChatSession.created_at.desc()).all()

    result = []
    for s in sessions:
        # get first user message as session title
        first_msg = db.query(Message).filter(
            Message.session_id == s.id,
            Message.role == "user"
        ).order_by(Message.created_at).first()

        result.append({
            "session_id": s.id,
            "title": first_msg.content[:40] + "..." if first_msg and len(first_msg.content) > 40 else (first_msg.content if first_msg else "New Chat"),
            "created_at": s.created_at.isoformat()
        })
    return result