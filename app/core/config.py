from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Приложение
    APP_NAME: str = "Literary Forum"
    DEBUG: bool = False

    # База данных
    DATABASE_URL: str
    DATABASE_URL_LOCAL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")


# Создаём один экземпляр на всё приложение
settings = Settings()