import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # App Config
    APP_NAME: str = "Career Architect Elite OS"
    DEBUG: bool = False
    
    # Paths
    # Ensures BASE_DIR points to the repo root, assuming config.py is in root
    BASE_DIR: Path = Field(default_factory=lambda: Path(__file__).resolve().parent)
    DATA_DIR: Path = Field(default_factory=lambda: Path(__file__).resolve().parent / "data")
    SCHEMA_DIR: Path = Field(default_factory=lambda: Path(__file__).resolve().parent / "schemas")
    LOG_DIR: Path = Field(default_factory=lambda: Path(__file__).resolve().parent / "logs")

    # LLM Configuration
    LLM_MODEL: str = Field(default="gemini-3-flash-preview", env="LLM_MODEL")
    GEMINI_API_KEY: str = Field(..., env="GEMINI_API_KEY") # Required field

    # Privacy / Regex Patterns
    REDACT_PATTERN: str = r'[\w\.-]+@[\w\.-]+'
    PHONE_PATTERN: str = r'\d[\d -]{8,12}\d'

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    def ensure_directories(self):
        """Create necessary directories if they don't exist."""
        self.LOG_DIR.mkdir(exist_ok=True)
        self.DATA_DIR.mkdir(exist_ok=True)

# Instantiate settings
try:
    settings = Settings()
    settings.ensure_directories()
except Exception as e:
    # Graceful fallback or hard fail depending on requirement. 
    # For a professional app, failing fast on missing config is better.
    raise RuntimeError(f"Failed to load configuration: {e}")
