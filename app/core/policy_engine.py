import redis
import json
import os

r = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, decode_responses=True)

POLICY_KEY = "active_policy"

def load_policy():
    policy = r.get(POLICY_KEY)
    if policy:
        return json.loads(policy)
    else:
        with open("policies/policy.json") as f:
            data = json.load(f)
            r.set(POLICY_KEY, json.dumps(data))
            return data
