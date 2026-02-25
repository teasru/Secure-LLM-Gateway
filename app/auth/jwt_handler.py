import os
from jose import jwt, JWTError
from datetime import datetime, timedelta

SECRET = os.getenv("JWT_SECRET", "devsecret")
ALGORITHM = "HS256"

def create_token(user_id: str, role: str):
    payload = {
        "sub": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=2)
    }
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
