"""
Application configuration using pydantic-settings.
All values are loaded from environment variables / .env file.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    APP_NAME: str = "SmartCampus AI"
    ENV: str = "development"
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # MySQL
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "smartcampus"
    DB_PASSWORD: str = "smartcampus_password"
    DB_NAME: str = "smartcampus_ai"
    DATABASE_URL: str = "mysql+pymysql://smartcampus:smartcampus_password@localhost:3306/smartcampus_ai"

    # Ollama / LLM
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"

    # RAG
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 100
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    VECTOR_STORE_PATH: str = "./vectordb"
    DOCUMENTS_PATH: str = "./documents"
    SIMILARITY_THRESHOLD: float = 0.35
    TOP_K_RESULTS: int = 5
    CONVERSATION_MEMORY_SIZE: int = 6

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
