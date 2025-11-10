# backend/storage.py
import os
import redis
import uuid
import json
from typing import Any, Optional

# Try Redis first, fallback to in-memory dict
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
try:
    r = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    r.ping()
    USE_REDIS = True
except Exception:
    print(" Redis not running. Using in-memory store.")
    r = None
    USE_REDIS = False

# In-memory fallback
_memory_store = {}


def save_session_data(session_id: str, key: str, value: Any, ttl: int = 3600):
    """
    Save data under a session_id + key (resume filename).
    TTL ensures auto-expiry (default 1 hour).
    """
    if USE_REDIS:
        # store in a Redis hash
        r.hset(session_id, key, json.dumps(value))
        r.expire(session_id, ttl)
    else:
        if session_id not in _memory_store:
            _memory_store[session_id] = {}
        _memory_store[session_id][key] = value


def get_session_data(session_id: str, key: str) -> Optional[Any]:
    """Fetch stored resume data for a given session_id + key."""
    if USE_REDIS:
        data = r.hget(session_id, key)
        return json.loads(data) if data else None
    return _memory_store.get(session_id, {}).get(key)


def list_session_keys(session_id: str):
    """List all resume keys stored under a session."""
    if USE_REDIS:
        return r.hkeys(session_id)
    return list(_memory_store.get(session_id, {}).keys())


def delete_session(session_id: str):
    """Delete all data for a session (manual cleanup)."""
    if USE_REDIS:
        r.delete(session_id)
    else:
        _memory_store.pop(session_id, None)
