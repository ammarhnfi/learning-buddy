# app/core/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Learning Buddy"
    GEMINI_API_KEY: str = "AIzaSyDA2AnvEcU3fhPSPktdZTHfx5fIlArZKpo"
    GEMINI_CHAT_MODEL: str = "gemini-2.5-flash"   # Anda menyebut ingin gemini flash 2-5
    EMBED_MODEL: str = "models/text-embedding-004"
    EMB_DIR: str = "app/embeddings"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()