from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.database import Base, engine
from routers import auth, chat
from services.weather import get_weather

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AnnaData API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)

@app.get("/")
def root():
    return {"status": "AnnaData backend running"}

@app.get("/weather")
async def weather():
    data = await get_weather(18.52, 73.85)  # Pune coordinates
    return {"forecast": data}