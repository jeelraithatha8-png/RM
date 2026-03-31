"""
Configuration for Nest & Found Backend.

Uses Pydantic Settings for environment-variable-based configuration
with .env file support and sensible defaults.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os


def _default_db_url():
    """Use /tmp/ for SQLite on Vercel (read-only filesystem), else local path."""
    if os.environ.get("VERCEL"):
        return "sqlite+aiosqlite:////tmp/nestfound.db"
    return "sqlite+aiosqlite:///./nestfound.db"


class Settings(BaseSettings):
    PROJECT_NAME: str = "Nest & Found Backend"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = Field(default="supersecretkey_please_change_in_production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str = Field(default_factory=_default_db_url)
    
    # Redis (set to "mock_redis" for in-memory mock, or a real redis:// URL)
    REDIS_URL: str = Field(default="mock_redis")

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )


settings = Settings()
