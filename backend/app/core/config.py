from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENVIRONMENT: str = "dev"
    DEBUG: bool = False
    SECRET_KEY: str
    ALLOWED_ORIGINS: str = ""
    DATABASE_URL: str
    REDIS_URL: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    EVOLUTION_API_URL: str
    EVOLUTION_API_KEY: str
    
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-3.5-flash"
    GEMINI_MAX_RPM: int = 15
    GEMINI_MAX_RPD: int = 1500
    
    SAAS_ADMIN_EMAIL: str
    SAAS_ADMIN_PASSWORD: str

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    @property
    def get_allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

settings = Settings()
