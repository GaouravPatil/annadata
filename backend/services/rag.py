import json
import os
import math
import re
from collections import Counter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "knowledge_base", "data")
KNOWLEDGE_FILE = os.path.join(KNOWLEDGE_DIR, "agricultural_knowledge.json")

knowledge_data = []

def load_knowledge():
    global knowledge_data
    if knowledge_data:
        return
    if not os.path.exists(KNOWLEDGE_FILE):
        print(f"Knowledge file not found: {KNOWLEDGE_FILE}")
        return
    with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
        knowledge_data = json.load(f)
    print(f"Loaded {len(knowledge_data)} knowledge entries")

def tokenize(text: str) -> list:
    return re.findall(r'\w+', text.lower())

def tfidf_score(query_tokens: list, doc_tokens: list, all_docs: list) -> float:
    score = 0.0
    doc_counter = Counter(doc_tokens)
    total_docs = len(all_docs)

    for token in query_tokens:
        tf = doc_counter.get(token, 0) / max(len(doc_tokens), 1)
        docs_with_token = sum(1 for d in all_docs if token in d)
        idf = math.log((total_docs + 1) / (docs_with_token + 1)) + 1
        score += tf * idf
    return score

def build_knowledge_base():
    load_knowledge()
    print(f"Knowledge base ready with {len(knowledge_data)} entries")

def search_knowledge_base(query: str, n_results: int = 3) -> str:
    load_knowledge()

    if not knowledge_data:
        return "Knowledge base not available."

    query_tokens = tokenize(query)
    all_doc_tokens = []

    for item in knowledge_data:
        text = f"{item['topic']} {item['content']}"
        all_doc_tokens.append(tokenize(text))

    scores = []
    for i, doc_tokens in enumerate(all_doc_tokens):
        score = tfidf_score(query_tokens, doc_tokens, all_doc_tokens)
        scores.append((score, i))

    scores.sort(reverse=True)
    top_results = scores[:n_results]

    if not top_results or top_results[0][0] == 0:
        return "No relevant information found."

    context = "Relevant agricultural information:\n\n"
    for score, idx in top_results:
        item = knowledge_data[idx]
        context += f"{item['topic']}:\n{item['content']}\n\n"

    return context
