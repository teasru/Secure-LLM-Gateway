import redis
import hashlib
import os

r = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, decode_responses=True)

def get_cache(prompt: str):
    key = hashlib.sha256(prompt.encode()).hexdigest()
    return r.get(f"cache:{key}")

def set_cache(prompt: str, response: str):
    key = hashlib.sha256(prompt.encode()).hexdigest()
    r.setex(f"cache:{key}", 300, response)
