from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Cartify API"
    APP_VERSION: str = "0.1.0"

    # Database
    DATABASE_URL: str = (
        "postgresql://cartify_user:secretpassword@localhost:5432/cartify_db"
    )

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Email (Mailhog for development)
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = "noreply@cartify.com"
    MAIL_PORT: int = 1025
    MAIL_HOST: str = "localhost"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = False
    MAIL_TLS: bool = False
    MAIL_SSL: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
