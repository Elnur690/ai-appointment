from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENVIRONMENT: str = "dev"
    DEBUG: bool = False
    SECRET_KEY: str = "dev-secret-key-change-in-prod"
    ALLOWED_ORIGINS: str = ""
    DATABASE_URL: str = "postgresql+asyncpg://appointment:appointment_secret@localhost:5432/ai_appointment"
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    EVOLUTION_API_URL: str = "http://localhost:8080"
    EVOLUTION_API_KEY: str = "dev-evolution-key"
    
    GEMINI_API_KEY: str = "dev-gemini-key"
    GEMINI_MODEL: str = "gemini-3.5-flash"
    GEMINI_MAX_RPM: int = 15
    GEMINI_MAX_RPD: int = 1500
    
    SAAS_ADMIN_EMAIL: str = "admin@platform.com"
    SAAS_ADMIN_PASSWORD: str = "admin123"


    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    @property
    def get_allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

settings = Settings()
