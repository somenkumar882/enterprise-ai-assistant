
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "mock-key")
    OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT", "http://localhost:8000")
    SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT", "http://localhost:8000")
    SEARCH_KEY = os.getenv("SEARCH_KEY", "mock-key")
    SEARCH_INDEX = os.getenv("SEARCH_INDEX", "mock-index")
    ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "localhost")
    ELASTICSEARCH_PORT = int(os.getenv("ELASTICSEARCH_PORT", "9200"))
    ELASTICSEARCH_USERNAME = os.getenv("ELASTICSEARCH_USERNAME", "elastic")
    ELASTICSEARCH_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD", "changeme")
    ELASTICSEARCH_INDEX = os.getenv("ELASTICSEARCH_INDEX", "documents")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

settings = Settings()
