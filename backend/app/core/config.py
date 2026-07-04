"""
PhishGuard AI — Application Configuration

Centralized configuration management using pydantic-settings.
All settings are loaded from environment variables or .env file.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=(
            str(Path(__file__).resolve().parent.parent.parent.parent / ".env"),
            str(Path(__file__).resolve().parent.parent.parent / ".env"),
            ".env",
        ),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────
    app_name: str = "PhishGuard AI"
    app_env: Literal["development", "staging", "production", "test"] = "development"
    app_debug: bool = True
    app_version: str = "1.0.0"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # ── Security ─────────────────────────────────────────────────
    jwt_secret_key: str = "change-this-in-production-use-openssl-rand-hex-32"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 1440  # 24 hours
    api_key_prefix: str = "phishguard_"

    # ── CORS ─────────────────────────────────────────────────────
    cors_origins: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    # ── Rate Limiting ────────────────────────────────────────────
    rate_limit_per_minute: int = 60
    rate_limit_scan_per_minute: int = 20

    # ── LLM Configuration ───────────────────────────────────────
    llm_provider: Literal["openai", "groq", "ollama", "mock"] = "mock"
    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_base_url: str = "https://api.openai.com/v1"
    llm_temperature: float = 0.3
    llm_max_tokens: int = 2000

    # ── AI Models ────────────────────────────────────────────────
    ml_model_path: str = "app/ai/models/saved"
    transformer_model_name: str = "distilbert-base-uncased"
    use_transformer: bool = False
    use_gpu: bool = False

    # ── MongoDB ──────────────────────────────────────────────────
    mongodb_url: str = ""
    mongodb_db_name: str = "phishguard"
    mongodb_max_pool_size: int = 50
    mongodb_server_selection_timeout_ms: int = 5000
    mongodb_use_mock: bool = False

    # ── Data ─────────────────────────────────────────────────────
    data_dir: str = "data"

    # ── Logging ──────────────────────────────────────────────────
    log_level: str = "INFO"
    log_format: Literal["json", "console"] = "console"

    # ── Paths ────────────────────────────────────────────────────
    @property
    def base_dir(self) -> Path:
        return Path(__file__).resolve().parent.parent.parent

    @property
    def data_path(self) -> Path:
        return self.base_dir / self.data_dir

    @property
    def model_save_path(self) -> Path:
        return self.base_dir / self.ml_model_path

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings singleton."""
    return Settings()
