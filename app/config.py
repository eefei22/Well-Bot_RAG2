# app/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "dev"
    log_level: str = "INFO"
    tz: str = "UTC"

    ollama_url: str = "http://localhost:11434"
    ollama_chat_model: str = "gemma3"
    ollama_embed_model: str = "nomic-embed-text"
    embedding_dim: int = 768
    embedding_similarity: str = "cosine"

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection_docs: str = "kb_docs"
    qdrant_collection_memory: str = "user_memory"

    session_backend: str = "memory"
    redis_url: str | None = None

    mongodb_uri: str = "placeholder"
    mongodb_db: str = "placeholder"
    mongodb_chat_collection: str = "placeholder"

    allowed_origins: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
