from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    PROJECT_NAME: str = "Nest & Found Backend"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = Field(default="supersecretkey_please_change_in_production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./nestfound.db")
    
    # Redis
    REDIS_URL: str = Field(default="mock_redis")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
