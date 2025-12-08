from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import re


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )
    
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000", "https://chatops.ufazien.com"]
    
    # API
    API_V1_STR: str = "/api/v1"
    
    # WebSocket
    WS_PATH: str = "/ws"
    
    @property
    def async_database_url(self) -> str:
        """Convert postgresql:// to postgresql+asyncpg:// for async SQLAlchemy
        and remove SSL parameters that asyncpg doesn't support in URL"""
        url = self.DATABASE_URL
        # Remove query parameters that asyncpg doesn't support in URL
        url = re.sub(r'[?&]sslmode=[^&]*', '', url)
        url = re.sub(r'[?&]channel_binding=[^&]*', '', url)
        # Clean up any trailing ? or &
        url = re.sub(r'[?&]+$', '', url)
        # Convert to asyncpg
        url = re.sub(r'^postgresql:', 'postgresql+asyncpg:', url)
        return url


settings = Settings()

