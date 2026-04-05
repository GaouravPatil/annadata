
import chromadb
import json
import os
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "knowledge_base", "data")
CHROMA_DIR = os.path.join(BASE_DIR, "knowledge_base", "chroma_db")
KNOWLEDGE_FILE = os.path.join(KNOWLEDGE_DIR, "agricultural_knowledge.json")

embedder = SentenceTransformer('all-MiniLM-L6-v2')
chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)

def get_or_create_collection():
    return chroma_client.get_or_create_collection(
        name="annadata_knowledge",
        metadata={"hnsw:space": "cosine"}
    )

def build_knowledge_base():
    collection = get_or_create_collection()

    if collection.count() > 0:
        print(f"Knowledge base already has {collection.count()} entries")
        return

    if not os.path.exists(KNOWLEDGE_FILE):
        print(f"File not found: {KNOWLEDGE_FILE}")
        return

    with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
        knowledge_data = json.load(f)

    print(f"Building knowledge base with {len(knowledge_data)} entries...")

    documents = []
    embeddings = []
    ids = []
    metadatas = []

    for i, item in enumerate(knowledge_data):
        text = f"{item['topic']}: {item['content']}"
        embedding = embedder.encode(text).tolist()
        documents.append(text)
        embeddings.append(embedding)
        ids.append(f"doc_{i}")
        metadatas.append({"topic": item["topic"]})

    collection.add(
        documents=documents,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas
    )
    print(f"Knowledge base built with {collection.count()} entries")

def search_knowledge_base(query: str, n_results: int = 3) -> str:
    try:
        collection = get_or_create_collection()

        if collection.count() == 0:
            return "Knowledge base not yet built."

        query_embedding = embedder.encode(query).tolist()

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

        if not results["documents"][0]:
            return "No relevant information found."

        context = "Relevant agricultural information:\n\n"
        for doc in results["documents"][0]:
            context += doc + "\n\n"

        return context
    except Exception as e:
        return f"Knowledge base search failed: {str(e)}"
