"""
Centralized application configuration.

All environment-driven settings live here so the rest of the codebase
never reads os.environ directly.
"""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root = two levels up from this file (backend/app/core/config.py -> backend/ -> root)
# Resolving paths this way means storage/DB locations are stable no matter
# where uvicorn or pytest is launched from.
PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- App ---
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # --- Storage ---
    database_url: str = f"sqlite:///{PROJECT_ROOT / 'storage' / 'app.db'}"
    audio_storage_dir: str = str(PROJECT_ROOT / "storage" / "audio")
    transcript_storage_dir: str = str(PROJECT_ROOT / "storage" / "transcripts")

    # --- Tier (drives which ASR/LLM providers get used) ---
    # free | mvp | scale | premium
    tier: str = "free"

    # --- ASR ---
    asr_engine: str = "faster_whisper"
    whisper_model_size: str = "base"

    # --- LLM ---
    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"

    openai_api_key: str | None = None
    anthropic_api_key: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()