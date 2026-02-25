import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "devsecret")
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    RATE_LIMIT: int = int(os.getenv("RATE_LIMIT", 10))
    RATE_WINDOW: int = int(os.getenv("RATE_WINDOW", 60))

settings = Settings()
