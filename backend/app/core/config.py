from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    app_name: str = "University Knowledge Search"
    app_env: str = "development"
    api_prefix: str = "/api/v1"

    auth_username: str = "student"
    auth_password: str = "practice2026"
    auth_secret_key: str = "change-this-secret-before-publication"
    auth_token_ttl_minutes: int = 480

    database_url: str = "postgresql+psycopg://knowledge:knowledge@postgres:5432/knowledge"
    elasticsearch_url: str = "http://elasticsearch:9200"
    elasticsearch_index: str = "documents"
    redis_url: str = "redis://redis:6379/0"
    redis_ttl_seconds: int = 300

    max_upload_mb: int = 20
    chunk_size: int = 1000
    chunk_overlap: int = 100
    cors_origins: str = Field(default="http://localhost:3000,http://localhost:5173")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        """Return CORS origins as a normalized list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()
