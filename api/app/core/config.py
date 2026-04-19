from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = "postgresql+psycopg://scada:scada_pass@localhost:5432/scada_db"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False

    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # ETL
    batch_size: int = 500
    dataset_seed: int = 42
    dataset_size: int = 2000

    # Pagination
    max_page_size: int = 100
    default_page_size: int = 20


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
