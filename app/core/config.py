from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Cartify API"
    APP_VERSION: str = "0.1.0"

    # Database
    DATABASE_URL: str = "sqlite:///./cartify.db"

    # Mail
    MAIL_HOST: str = "localhost"
    MAIL_PORT: int = 1025
    MAIL_FROM: str = "no-reply@cartify.local"

    class Config:
        env_file = ".env"


settings = Settings()
