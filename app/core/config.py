"""
Configuration settings for the Real Estate API.

This module contains all configuration settings using Pydantic Settings
for environment variable management and type safety.
"""

from typing import List
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    APP_NAME: str = "Real Estate API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # API Key (for external service authentication)
    API_KEY_HEADER: str = "X-API-Key"
    API_KEYS: List[str] = Field(default_factory=list, description="Valid API keys")
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "password"
    DB_NAME: str = "real_estate"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # External APIs
    EXTERNAL_API_TIMEOUT: int = 30
    EXTERNAL_API_RETRY_ATTEMPTS: int = 3
    
    # Threading
    MAX_WORKERS: int = 4
    THREAD_POOL_SIZE: int = 10

    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL from components."""
        return (
            f"mysql+mysqlconnector://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @validator("API_KEYS", pre=True)
    @classmethod
    def validate_api_keys(cls, v) -> List[str]:
        """Parse API keys from comma-separated string or list."""
        if isinstance(v, str):
            if v.strip() == "":
                return []
            return [key.strip() for key in v.split(",") if key.strip()]
        elif v is None:
            return []
        return v

    @validator("ALLOWED_HOSTS", pre=True)
    @classmethod
    def validate_allowed_hosts(cls, v) -> List[str]:
        """Parse ALLOWED_HOSTS from comma-separated string or list."""
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            return [host.strip() for host in v.split(",") if host.strip()]
        return v

    @validator("ALLOWED_ORIGINS", pre=True)
    @classmethod
    def validate_allowed_origins(cls, v) -> List[str]:
        """Parse ALLOWED_ORIGINS from comma-separated string or list."""
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings() 