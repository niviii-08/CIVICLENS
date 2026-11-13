import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    BACKEND_ROOT_URL: str = os.getenv("BACKEND_ROOT_URL", "http://localhost:5000")
    BACKEND_API_URL: str = os.getenv("BACKEND_API_URL", f"{BACKEND_ROOT_URL}/api")

settings = Settings()
