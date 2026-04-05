FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p knowledge_base/data knowledge_base/chroma_db

EXPOSE 8000

CMD ["python", "start.py"]
