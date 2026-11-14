from urllib.parse import quote_plus
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "dev"
    DEBUG: bool = False
    PLATFORM_DOMAIN: str = "randevu.vip"
    SECRET_KEY: str = "dev-secret-key-change-in-prod"
    ALLOWED_ORIGINS: str = (
        "https://randevu.vip,https://www.randevu.vip,"
        "https://admin.randevu.vip,https://app.randevu.vip,https://api.randevu.vip,"
        "http://localhost:22300,http://localhost:22301"
    )
    POSTGRES_USER: str = "appointment"
    POSTGRES_PASSWORD: str = "appointment_secret"
    POSTGRES_DB: str = "ai_appointment"
    DATABASE_URL: str = "postgresql+asyncpg://appointment:appointment_secret@postgres:5432/ai_appointment"
    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ALGORITHM: str = "HS256"

    EVOLUTION_API_URL: str = "http://evolution-api:22880"
    EVOLUTION_API_KEY: str = "dev-evolution-key"

    GEMINI_API_KEY: str = "dev-gemini-key"
    GEMINI_MODEL: str = "gemini-3.5-flash"
    GEMINI_MAX_RPM: int = 15
    GEMINI_MAX_RPD: int = 1500

    SAAS_ADMIN_EMAIL: str = "admin@randevu.vip"
    SAAS_ADMIN_PASSWORD: str = "admin123"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @model_validator(mode="after")
    def sync_database_url_with_postgres_env(self) -> "Settings":
        """Ensure DATABASE_URL always uses POSTGRES_USER / POSTGRES_PASSWORD / POSTGRES_DB from .env."""
        if "@" in self.DATABASE_URL and self.POSTGRES_USER and self.POSTGRES_PASSWORD:
            host_part = self.DATABASE_URL.split("@", 1)[1].split("/", 1)[0]
            encoded_user = quote_plus(self.POSTGRES_USER)
            encoded_pw = quote_plus(self.POSTGRES_PASSWORD)
            self.DATABASE_URL = f"postgresql+asyncpg://{encoded_user}:{encoded_pw}@{host_part}/{self.POSTGRES_DB}"
        return self

    @property
    def get_allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


settings = Settings()
