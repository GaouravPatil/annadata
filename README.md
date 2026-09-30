<div align="center">

# 🌾 ANNADATA
### *अन्नदाता — The One Who Feeds the World*

**Empowering India's farmers with AI-driven insights, from soil to sale.**

[![Frontend: React](https://img.shields.io/badge/Frontend-React-61DAFB?style=for-the-badge&logo=react&logoColor=white)](https://reactjs.org/)
[![Backend: FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![AI: Groq](https://img.shields.io/badge/AI-Groq-FF6B35?style=for-the-badge&logo=python&logoColor=white)](https://groq.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

---

> 🏆 *Built with passion for India's 140 million farmers.*

</div>

---

## 🚜 The Problem

India's farmers face a brutal trifecta every single season:
- **What to grow?** — No data-backed guidance on which crops suit their soil and climate.
- **Is my crop healthy?** — Pest / disease advice is hard to get in time.
- **Am I getting a fair deal?** — No transparent mandi prices before selling.

**Annadata fixes all of that.** In one chat app.

---

## ⚡ Features (what actually exists)

### 💬 Chat API
> JWT-protected chat with per-farmer sessions and history (`POST /chat`, `GET /sessions`, `GET /history/{session_id}`, `DELETE /sessions/{session_id}`). Last 10 messages cached in-memory (2h TTL), full history in DB.

### 🧅 Mandi Prices
> Live prices from `api.data.gov.in` (resource `9ef84268-...`). Triggered when the message mentions price/market/mandi/sell/rate/cost + a crop (wheat, rice, onion, tomato, cotton, sugarcane, soybean, maize). Defaults to Maharashtra, top 5 records with min/max/modal price.

### 🌦️ Weather API
> 7-day forecast from Open-Meteo (`temperature_2m_max/min`, `precipitation_sum`, `Asia/Kolkata`). Triggered by weather/rain/forecast/irrigation words **plus** farmer location.

### 📍 Location API
> Browser geolocation (`navigator.geolocation`) sent as `latitude`/`longitude` with every `/chat` request. Stored in prompt context as `Maharashtra, India region`.

### 📚 Farming Knowledge (RAG-lite)
> TF-IDF search over `backend/knowledge_base/data/agricultural_knowledge.json` (10 entries: PM-Kisan, PMFBY insurance, Soil Health Card, Wheat/Rice/Onion/Tomato guides, Pest Control, Storage, Kisan Call Centre). Triggered by scheme/insurance/pest/disease/fertilizer/cultivation words or any mentioned crop.

### 👤 Farmer Auth
> Simple `POST /register` (`name`, `location`, `age`, `language`) returning a JWT (`farmer_id`). No password — token stored in `localStorage`.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| 🖥️ Frontend | React 19 + Vite, `axios`, `react-markdown` |
| ⚙️ Backend | FastAPI + Uvicorn, SQLAlchemy + Alembic, Pydantic, `python-jose` (JWT) |
| 🤖 AI | Groq `llama-3.3-70b-versatile` via `services/agent.py` |
| 🌐 APIs | Open-Meteo (weather), data.gov.in (mandi), browser Geolocation |
| 🗄️ DB | SQLite locally (`annadata.db`), Postgres via `DATABASE_URL` (`psycopg2-binary`) |
| ⚡ Cache | `cachetools.TTLCache` (500 sessions, 2h TTL) |

---

## 🚀 Getting Started (local only)

> No deploy configured — everything runs on `localhost`.

### Prerequisites
- Python `3.11`
- Node.js `v16+` + npm

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # fill in GROQ_API_KEY, SECRET_KEY
# DATABASE_URL defaults to sqlite:///./annadata.db — no Postgres needed locally

python start.py                 # serves on http://localhost:8000
# alternative: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend

```bash
cd frontend
npm install

cp .env.example .env            # defaults to VITE_API_URL=http://localhost:8000
npm run dev                     # Vite dev server, open the printed localhost URL
```

### Environment Variables

Backend (`backend/.env`):

```env
DATABASE_URL=sqlite:///./annadata.db
SECRET_KEY=change-me-local-secret
GROQ_API_KEY=your_groq_api_key
DATA_GOV_API_KEY=579b464db66ec23bdd000001cdd3946e44ce4aad38534209a181d0
PORT=8000
```

Frontend (`frontend/.env`):

```env
VITE_API_URL=http://localhost:8000
```

---

## 🔌 API Endpoints

| Method | Path | Auth | Body / Notes |
|---|---|---|---|
| `GET` | `/` | — | `{ "status": "AnnaData backend running" }` |
| `POST` | `/register` | — | `{ name, location, age, language }` → `{ token, farmer_id }` |
| `POST` | `/chat` | Bearer JWT | `{ message, session_id?, latitude?, longitude? }` → `{ reply, session_id }` |
| `GET` | `/history/{session_id}` | Bearer JWT | `[{ role, content }]` |
| `GET` | `/sessions` | Bearer JWT | `[{ session_id, title, created_at }]` |
| `DELETE` | `/sessions/{session_id}` | Bearer JWT | `{ "status": "deleted" }` |

DB tables (auto-created on startup via `Base.metadata.create_all`): `farmers`, `sessions`, `messages`. Alembic migrations in `backend/migrations/` are kept for Postgres use.

---

## 📁 Project Structure

```
annadata/
├── frontend/               # React + Vite
│   ├── src/
│   │   ├── App.jsx         # Auth <-> Chat switch
│   │   ├── main.jsx
│   │   ├── index.css
│   │   └── components/
│   │       ├── Auth.jsx    # POST /register
│   │       └── Chat.jsx    # POST /chat + location + sessions
│   ├── public/
│   │   └── favicon.svg
│   ├── vite.config.js
│   ├── eslint.config.js
│   └── package.json
├── backend/                # FastAPI
│   ├── main.py             # app + CORS + lifespan
│   ├── start.py            # local entrypoint (PORT env, default 8000)
│   ├── requirements.txt    # 11 pinned deps, no bloat
│   ├── Dockerfile          # optional local docker (not a deploy target)
│   ├── .dockerignore
│   ├── alembic.ini
│   ├── migrations/         # Postgres migrations
│   ├── models/
│   │   └── database.py     # Farmer / Session / Message, sqlite fallback
│   ├── routers/
│   │   ├── auth.py         # POST /register
│   │   └── chat.py         # /chat, /sessions, /history
│   ├── services/
│   │   ├── agent.py        # Groq + mandi + weather + RAG orchestration
│   │   ├── weather.py      # Open-Meteo client
│   │   ├── rag.py          # TF-IDF over agricultural_knowledge.json
│   │   └── cache.py        # TTL session cache
│   └── knowledge_base/
│       ├── scraper.py      # static knowledge generator
│       └── data/
│           └── agricultural_knowledge.json
├── LICENSE
└── README.md
```

> Removed as dead code: root `requirements.txt` (175-line langchain/torch dump), `chroma_db/`, nested `knowledge_base/knowledge_base/`, Vite boilerplate (`App.css`, `assets/`, `icons.svg`), Datadog workflow, Railway/Heroku deploy files (`Procfile`, `nixpacks.toml`, `runtime.txt`, `.railwayignore`), empty `.env` files. Single root `.gitignore` now covers backend + frontend.

---

## 🌍 Impact

> *"There are 140 million farmers in India. Each one deserves access to the same intelligence that large agricultural corporations have."*

Annadata democratizes precision agriculture — no expensive equipment, no agronomist on speed dial. Just a phone and a will to grow.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

```bash
# Create your feature branch
git checkout -b feature/AmazingFeature

# Commit your changes
git commit -m 'Add some AmazingFeature'

# Push and open a PR
git push origin feature/AmazingFeature
```

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<div align="center">

**Made with ❤️ for the backbone of India.**

*Jai Kisan. 🌾*

</div>
