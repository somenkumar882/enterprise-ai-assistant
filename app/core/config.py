
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "mock-key")
    OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT", "http://localhost:8000")
    SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT", "http://localhost:8000")
    SEARCH_KEY = os.getenv("SEARCH_KEY", "mock-key")
    SEARCH_INDEX = os.getenv("SEARCH_INDEX", "mock-index")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

settings = Settings()
