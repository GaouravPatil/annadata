FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p knowledge_base/data knowledge_base/chroma_db

CMD uvicorn main:app --host 0.0.0.0 --port $PORT
