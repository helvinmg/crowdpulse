from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_ENV: str = "development"
    LOG_LEVEL: str = "DEBUG"
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001"

    # Database (supports PostgreSQL and MySQL)
    # PostgreSQL: postgresql://postgres:password@localhost:5432/crowdpulse
    # MySQL:      mysql+pymysql://root:password@localhost:3306/crowdpulse
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/crowdpulse"

    # Redis (optional — only needed for Celery scheduled pipeline)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Telegram
    TELEGRAM_API_ID: str = ""
    TELEGRAM_API_HASH: str = ""
    TELEGRAM_SESSION_NAME: str = "crowdpulse"

    # Twitter / X
    TWITTER_BEARER_TOKEN: str = ""

    # Reddit
    REDDIT_CLIENT_ID: str = ""
    REDDIT_CLIENT_SECRET: str = ""

    # Auth
    JWT_SECRET: str = "change-me-to-a-random-secret-key"
    JWT_EXPIRY_HOURS: int = 72

    # LLM Labeling (Google Gemini — free tier)
    # Get your key at: https://aistudio.google.com/apikey
    GEMINI_API_KEY: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
