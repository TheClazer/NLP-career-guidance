import logging
import time
import json
import os
from typing import Dict, Any, Optional

from config import settings
from utils.json_utils import safe_load_json_from_text
from utils.validator import validate_json
from utils.logging_config import logger
from dotenv import load_dotenv

# Load all env vars so os.getenv finds the backup keys
load_dotenv(settings.BASE_DIR / ".env")

MAX_RETRIES = 3

# Key Rotation State
_CURRENT_KEY_IDX = 0
_KEYS = []

def _init_keys():
    """Initialize the pool of available API keys."""
    global _KEYS
    if _KEYS:
        return
        
    # Primary Key
    if settings.GEMINI_API_KEY:
        _KEYS.append(settings.GEMINI_API_KEY)
        
    # Backup Keys (GEMINI_API_KEY_2, _3, _4...)
    for i in range(2, 6):
        k = os.getenv(f"GEMINI_API_KEY_{i}")
        if k:
            _KEYS.append(k)
            
    logger.info(f"Loaded {len(_KEYS)} API keys for rotation.")

def rotate_key():
    """Switch to the next available API key."""
    global _CURRENT_KEY_IDX
    _init_keys()
    
    if not _KEYS:
        logger.error("No API keys available to rotate.")
        return False
        
    _CURRENT_KEY_IDX = (_CURRENT_KEY_IDX + 1) % len(_KEYS)
    new_key = _KEYS[_CURRENT_KEY_IDX]
    masked = f"{new_key[:4]}...{new_key[-4:]}"
    logger.warning(f"Rotating to API Key #{_CURRENT_KEY_IDX + 1} ({masked})")
    
    import google.generativeai as genai
    genai.configure(api_key=new_key)
    return True

def get_genai_model():
    """Lazy load GenAI."""
    _init_keys()
    import google.generativeai as genai
    
    # Configure with current correct key
    current_key = _KEYS[_CURRENT_KEY_IDX] if _KEYS else settings.GEMINI_API_KEY
    if not current_key:
         current_key = os.getenv("GEMINI_API_KEY")
    
    masked = f"{current_key[:4]}...{current_key[-4:]}" if current_key else "None"
    # logger.debug(f"Getting model with key: {masked}") # Verbose
         
    genai.configure(api_key=current_key)
    
    return genai.GenerativeModel(settings.LLM_MODEL)

def call_llm_with_schema(prompt: str, schema_path: str, timeout: int = 15) -> Dict[str, Any]:
    """
    Call LLM with automatic key rotation on 429 errors.
    """
    if not settings.GEMINI_API_KEY and not os.getenv("GEMINI_API_KEY"):
         # Check if we have backups at least
         pass 

    last_err = None
    
    # We retry a bit more to allow for key rotation
    # If we have 3 keys, we want to try at least 3 times + retries
    total_attempts = MAX_RETRIES + 4 # ample attempts for rotation
    
    for attempt in range(total_attempts):
        try:
            model = get_genai_model()
            logger.debug(f"LLM Call Attempt {attempt+1}/{total_attempts}")
            
            resp = model.generate_content(prompt)
            raw = resp.text
            
            # Parse
            try:
                obj = safe_load_json_from_text(raw)
                if not isinstance(obj, dict):
                    raise ValueError("LLM returned a list or primitive, expected JSON object.")
            except Exception as e:
                # Parse error isn't a quota error, so simplified retry logic
                last_err = f"JSON parse error: {e}"
                logger.warning(f"Parse Fail: {e}")
                time.sleep(1)
                continue
            
            # Validate
            try:
                with open(schema_path, "r", encoding='utf-8') as f:
                    schema = json.load(f)
            except Exception as e:
                raise RuntimeError(f"Failed to load user schema at {schema_path}: {e}")

            ok, err = validate_json(obj, schema)
            if ok:
                return obj
                
            last_err = f"Validation error: {err}"
            logger.warning(f"Schema Val Fail: {err}")
            
        except Exception as e:
            err_str = str(e)
            last_err = f"LLM error: {err_str}"
            logger.error(f"LLM error: {e}")
            
            # Key Rotation Trigger
            if "429" in err_str or "quota" in err_str.lower():
                logger.warning("Quota hit! Attempting key rotation...")
                if rotate_key():
                    time.sleep(1) # Brief pause after switch
                    continue
            
        time.sleep(1) # Backoff
        
    raise RuntimeError(f"LLM failed after {total_attempts} attempts. Last error: {last_err}")
