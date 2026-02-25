from fastapi import APIRouter
import redis
import os
import json

router = APIRouter()
r = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, decode_responses=True)

@router.post("/policy")
def update_policy(new_policy: dict):
    r.set("active_policy", json.dumps(new_policy))
    return {"status": "Policy updated"}
