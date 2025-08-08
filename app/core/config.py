"""
Configuration settings for the Real Estate API.

This module contains all configuration settings using Pydantic Settings
for environment variable management and type safety.
"""

import os
from typing import List

from pydantic import ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application
    app_name: str = "Real Estate API"
    app_version: str = "1.0.0"
    debug: bool = True
    environment: str = "development"

    # API Key (for external service authentication)
    api_key_header: str = "X-API-Key"
    api_keys: List[str] = Field(default_factory=list, description="Valid API keys")

    # CORS
    allowed_hosts: List[str] = ["*"]
    allowed_origins: List[str] = ["*"]
    allowed_methods: List[str] = ["*"]
    allowed_headers: List[str] = ["*"]

    # Database
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = "password"
    db_name: str = "real_estate"

    # Direct Database URL (for Lambda)
    database_url: str = ""

    # AWS VPC Configuration
    vpc_security_group_id: str = ""
    vpc_subnet_id_1: str = ""
    vpc_subnet_id_2: str = ""

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # External APIs
    external_api_timeout: int = 30
    external_api_retry_attempts: int = 3

    # Threading
    max_workers: int = 4
    thread_pool_size: int = 10

    @property
    def get_database_url(self) -> str:
        """Get database URL from environment or construct from components."""
        if self.database_url:
            return self.database_url
        return f"mysql+mysqlconnector://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @field_validator("thread_pool_size", mode="before")
    @classmethod
    def validate_thread_pool_size(cls, v):
        """Validate and clean thread_pool_size value."""
        if isinstance(v, str):
            import re

            match = re.search(r"^(\d+)", v.strip())
            if match:
                return int(match.group(1))
            return 10
        return v

    @field_validator("db_port", mode="before")
    @classmethod
    def validate_db_port(cls, v):
        """Validate and clean db_port value."""
        if isinstance(v, str):
            import re

            match = re.search(r"^(\d+)", v.strip())
            if match:
                return int(match.group(1))
            return 3306
        return v

    @field_validator("external_api_timeout", mode="before")
    @classmethod
    def validate_external_api_timeout(cls, v):
        """Validate and clean external_api_timeout value."""
        if isinstance(v, str):
            import re

            match = re.search(r"^(\d+)", v.strip())
            if match:
                return int(match.group(1))
            return 30
        return v

    @field_validator("external_api_retry_attempts", mode="before")
    @classmethod
    def validate_external_api_retry_attempts(cls, v):
        """Validate and clean external_api_retry_attempts value."""
        if isinstance(v, str):
            import re

            match = re.search(r"^(\d+)", v.strip())
            if match:
                return int(match.group(1))
            return 3
        return v

    @field_validator("max_workers", mode="before")
    @classmethod
    def validate_max_workers(cls, v):
        """Validate and clean max_workers value."""
        if isinstance(v, str):
            import re

            match = re.search(r"^(\d+)", v.strip())
            if match:
                return int(match.group(1))
            return 4
        return v

    @field_validator("api_keys", mode="before")
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

    @field_validator("allowed_hosts", mode="before")
    @classmethod
    def validate_allowed_hosts(cls, v) -> List[str]:
        """Parse allowed_hosts from comma-separated string or list."""
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            return [host.strip() for host in v.split(",") if host.strip()]
        return v

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def validate_allowed_origins(cls, v) -> List[str]:
        """Parse allowed_origins from comma-separated string or list."""
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    model_config = ConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="allow"
    )


# Global settings instance
settings = Settings()
