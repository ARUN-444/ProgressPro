"""
Application configuration module.
Loads settings from environment variables and .env file using Pydantic Settings.
"""

from typing import List
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application settings.
    Values can be overridden using environment variables or a .env file.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application Info
    APP_NAME: str = "ProgressPro: Fitness Progress Analysis & Recommendation API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"

    # Security & JWT Authentication
    # Note: For production, generate a secure random string (e.g. secrets.token_hex(32))
    SECRET_KEY: str = "dev-secret-key-change-me-in-production-progresspro"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # MySQL Database Configuration
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "progresspro_db"

    # Optional full database connection URL override (useful for testing or custom connection strings)
    DATABASE_URL: str | None = None

    # CORS Allowed Origins
    CORS_ORIGINS: List[str] = ["*"]

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """
        Builds the SQLAlchemy connection URI.
        Uses DATABASE_URL if provided; otherwise constructs standard MySQL connection using PyMySQL.
        """
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


# Global settings singleton instance
settings = Settings()
