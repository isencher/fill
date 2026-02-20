"""
Centralized application settings using pydantic-settings.

All configuration values are loaded from environment variables
with sensible defaults for development.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings."""

    # Application
    app_name: str = "Fill API"
    app_version: str = "0.1.0"
    debug: bool = False

    # Database
    database_url: str = "sqlite:///./data/fill.db"
    pool_size: int = 20
    max_overflow: int = 40
    pool_timeout: int = 30
    pool_recycle: int = 1800

    # File Upload
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: list[str] = [".xlsx", ".csv"]
    upload_ttl_hours: int = 24

    # CORS
    allowed_origins: list[str] = ["http://localhost:8000", "http://localhost:3000"]

    # Security
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
