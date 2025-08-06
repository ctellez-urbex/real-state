"""
Configuration settings for the Real Estate API.

This module contains all configuration settings using Pydantic Settings
for environment variable management and type safety.
"""

import os
from typing import List
from pydantic import Field, field_validator, ConfigDict
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

    @field_validator("THREAD_POOL_SIZE", mode="before")
    @classmethod
    def validate_thread_pool_size(cls, v):
        """Validate and clean THREAD_POOL_SIZE value."""
        if isinstance(v, str):
            # Extract only the numeric part if there's concatenation
            import re
            match = re.search(r'^(\d+)', v.strip())
            if match:
                return int(match.group(1))
            # If no number found, return default
            return 10
        return v

    @field_validator("DB_PORT", mode="before")
    @classmethod
    def validate_db_port(cls, v):
        """Validate and clean DB_PORT value."""
        if isinstance(v, str):
            # Extract only the numeric part if there's concatenation
            import re
            match = re.search(r'^(\d+)', v.strip())
            if match:
                return int(match.group(1))
            # If no number found, return default
            return 3306
        return v

    @field_validator("EXTERNAL_API_TIMEOUT", mode="before")
    @classmethod
    def validate_external_api_timeout(cls, v):
        """Validate and clean EXTERNAL_API_TIMEOUT value."""
        if isinstance(v, str):
            # Extract only the numeric part if there's concatenation
            import re
            match = re.search(r'^(\d+)', v.strip())
            if match:
                return int(match.group(1))
            # If no number found, return default
            return 30
        return v

    @field_validator("EXTERNAL_API_RETRY_ATTEMPTS", mode="before")
    @classmethod
    def validate_external_api_retry_attempts(cls, v):
        """Validate and clean EXTERNAL_API_RETRY_ATTEMPTS value."""
        if isinstance(v, str):
            # Extract only the numeric part if there's concatenation
            import re
            match = re.search(r'^(\d+)', v.strip())
            if match:
                return int(match.group(1))
            # If no number found, return default
            return 3
        return v

    @field_validator("MAX_WORKERS", mode="before")
    @classmethod
    def validate_max_workers(cls, v):
        """Validate and clean MAX_WORKERS value."""
        if isinstance(v, str):
            # Extract only the numeric part if there's concatenation
            import re
            match = re.search(r'^(\d+)', v.strip())
            if match:
                return int(match.group(1))
            # If no number found, return default
            return 4
        return v

    @field_validator("API_KEYS", mode="before")
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

    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def validate_allowed_hosts(cls, v) -> List[str]:
        """Parse ALLOWED_HOSTS from comma-separated string or list."""
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            return [host.strip() for host in v.split(",") if host.strip()]
        return v

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def validate_allowed_origins(cls, v) -> List[str]:
        """Parse ALLOWED_ORIGINS from comma-separated string or list."""
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# Global settings instance
settings = Settings() 