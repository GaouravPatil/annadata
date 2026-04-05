
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from models.database import Base, engine
from routers import auth, chat

@asynccontextmanager
async def lifespan(app: FastAPI):
    from services.rag import build_knowledge_base
    build_knowledge_base()
    yield

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AnnaData API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)

@app.get("/")
def root():
    return {"status": "AnnaData backend running"}
