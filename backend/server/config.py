from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:pg123456@localhost:5432/food_time"
    REDIS_URL: str = "redis://localhost:6379/0"

    SECRET_KEY: str = "change-me-to-a-256-bit-secret-key-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_DAYS: int = 30

    WX_APPID: str = ""
    WX_SECRET: str = ""
    WX_EXPIRY_TMPL_ID: str = ""

    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 10

    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()