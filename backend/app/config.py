"""
Configuration module for Multi-Agent Lead Generation System.
Loads environment variables using Pydantic Settings.
"""

from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""

    # Application & URLs
    app_url: str = "http://localhost:8000"
    dashboard_url: str = "http://localhost:5173"
    api_prefix: str = "/api"

    # CORS: extra comma-separated origins, plus a regex that by default allows
    # localhost and private-network IPs on any port (for LAN dashboard access).
    cors_origins: str = ""
    cors_origin_regex: str = (
        r"^https?://(localhost|127\.0\.0\.1|0\.0\.0\.0|10(\.\d{1,3}){3}"
        r"|192\.168(\.\d{1,3}){2}|172\.(1[6-9]|2\d|3[01])(\.\d{1,3}){2})(:\d+)?$"
    )

    # Database
    database_url: str = "sqlite+aiosqlite:///./leadgen.db"

    # LLM Settings
    llm_provider: str = "groq"
    llm_api_key: Optional[str] = None
    llm_model: str = "llama-3.3-70b-versatile"
    llm_fallback_to_mock: bool = True

    # Scheduler Settings
    scheduler_enabled: bool = True
    schedule_interval_hours: int = 6

    # Scraper & Rate Limits
    scraper_headless: bool = True
    scraper_timeout_ms: int = 25000
    max_scraped_per_run: int = 10

    # User & Outreach Defaults
    sender_name: str = "Web Architecture Team"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """Return cached singleton settings instance."""
    return Settings()
