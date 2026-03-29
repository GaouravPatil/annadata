from sqlalchemy import create_engine, Column, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Farmer(Base):
    __tablename__ = "farmers"
    id = Column(String, primary_key=True)
    name = Column(String)
    phone = Column(String, unique=True)
    language = Column(String, default="en")
    location = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Session(Base):
    __tablename__ = "sessions"
    id = Column(String, primary_key=True)
    farmer_id = Column(String, ForeignKey("farmers.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class Message(Base):
    __tablename__ = "messages"
    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("sessions.id"))
    role = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()