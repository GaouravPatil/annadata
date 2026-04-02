from cachetools import TTLCache

# 500 sessions, 2 hour expiry
session_cache = TTLCache(maxsize=500, ttl=7200)

def get_session_history(session_id: str) -> list:
    return session_cache.get(session_id, [])

def add_to_session(session_id: str, role: str, content: str):
    if session_id not in session_cache:
        session_cache[session_id] = []
    # keep only last 10 messages in cache to save memory
    session_cache[session_id].append({"role": role, "content": content})
    if len(session_cache[session_id]) > 10:
        session_cache[session_id] = session_cache[session_id][-10:]

def clear_session(session_id: str):
    if session_id in session_cache:
        del session_cache[session_id]

