from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Starting AnnaData...")
        from models.database import Base, engine
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created")
        from services.rag import build_knowledge_base
        build_knowledge_base()
        logger.info("Knowledge base ready")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise
    yield

from models.database import Base, engine
from routers import auth, chat

app = FastAPI(title="AnnaData API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)

@app.get("/")
def root():
    return {"status": "AnnaData backend running"}
