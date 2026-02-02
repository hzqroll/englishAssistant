"""
Application Configuration Settings

Uses Pydantic Settings to manage environment variables and configuration.
"""

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = Field(
        default="mysql+pymysql://zcy_file_transfer:NHb475%26%23g@pc-bp1b369uwz9g08g1d.mysql.polardb.rds.aliyuncs.com:3306/db_file_transfer?charset=utf8mb4",
        description="MySQL database connection URL",
    )
    DATABASE_POOL_SIZE: int = Field(default=20, description="Database connection pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=10, description="Database max overflow connections")

    # Zhipu AI
    ZHIPUAI_API_KEY: str = Field(default="", description="Zhipu AI API key")
    ZHIPUAI_MODEL: str = Field(default="glm-4-flash", description="Zhipu AI model to use")
    ZHIPUAI_TIMEOUT: int = Field(default=30, description="Zhipu AI request timeout in seconds")
    ZHIPUAI_MAX_RETRIES: int = Field(default=3, description="Zhipu AI max retry attempts")

    # Security
    SECRET_KEY: str = Field(
        default="change-this-secret-key-in-production",
        description="Secret key for cryptographic operations",
    )
    JWT_SECRET_KEY: str = Field(
        default="change-this-secret-key-in-production",
        description="JWT secret key for token signing",
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, description="Access token expiration in minutes"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7, description="Refresh token expiration in days"
    )

    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:8000"],
        description="Allowed CORS origins",
    )

    # Application
    LOG_LEVEL: str = Field(default="INFO", description="Application log level")
    ENVIRONMENT: str = Field(
        default="development", description="Environment (development/production)"
    )
    DEBUG: bool = Field(default=True, description="Debug mode")
    API_V1_PREFIX: str = Field(default="/api/v1", description="API v1 prefix")

    # Rate Limiting
    RATE_LIMIT_ANONYMOUS: str = Field(default="5/hour", description="Anonymous user rate limit")
    RATE_LIMIT_FREE: str = Field(default="50/day", description="Free user rate limit")
    RATE_LIMIT_PAID: str = Field(default="500/day", description="Paid user rate limit")

    # Cache (in-memory for V1 MVP)
    CACHE_ENABLED: bool = Field(default=True, description="Enable caching")
    CACHE_TTL: int = Field(default=86400, description="Cache TTL in seconds (24 hours)")
    CACHE_MAX_SIZE: int = Field(default=1000, description="Maximum cache entries")

    # File Upload
    MAX_TEXT_LENGTH: int = Field(default=5000, description="Maximum text length in characters")
    MAX_FILE_SIZE: int = Field(default=10485760, description="Maximum file size in bytes (10MB)")

    # LanguageTool
    LANGUAGETOOL_LANGUAGE: str = Field(default="en-US", description="LanguageTool language")
    LANGUAGETOOL_MAX_ERRORS: int = Field(default=100, description="Maximum errors to detect")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
