from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    project_name: str = 'UnderwriteAI Backend'
    api_v1_str: str = '/api/v1'
    environment: str = 'development'

    database_url: str = 'postgresql+psycopg2://underwrite:underwrite@localhost:5432/underwrite_ai'
    create_tables_on_startup: bool = True

    llm_provider: str = 'ollama'
    llm_model: str = 'llama3.1:8b'
    ollama_base_url: str = 'http://localhost:11434'
    ollama_request_timeout_seconds: int = 120
    groq_api_key: str = ''
    groq_model: str = 'llama-3.1-8b-instant'

    embedding_model: str = 'nomic-embed-text'
    vector_db_path: str = 'chroma_db'
    enable_vector_store: bool = True

    cors_origins: List[str] = Field(default_factory=lambda: ['http://localhost:3000', 'http://127.0.0.1:3000'])

    uploads_dir: str = 'uploads'


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
