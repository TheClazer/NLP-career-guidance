import os
import pytest
from pathlib import Path
from config import Settings

def test_settings_defaults():
    # Test loading with minimum requirement (API KEY)
    # We mock the environment to safe values
    os.environ["GEMINI_API_KEY"] = "fake_key"
    settings = Settings()
    
    assert settings.APP_NAME == "Career Architect Elite OS"
    assert settings.DEBUG is False
    assert settings.LLM_MODEL == "gemini-3-pro-review"
    assert isinstance(settings.BASE_DIR, Path)
    assert isinstance(settings.LOG_DIR, Path)

def test_missing_api_key():
    # Unset critical key and verify error
    if "GEMINI_API_KEY" in os.environ:
        del os.environ["GEMINI_API_KEY"]
        
    with pytest.raises(Exception): # Pydantic validation error or similar
        Settings()
