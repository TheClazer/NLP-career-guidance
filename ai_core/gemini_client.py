import logging
import time
import json
from typing import Dict, Any, Optional

from config import settings
from utils.json_utils import safe_load_json_from_text
from utils.validator import validate_json
from utils.logging_config import logger

MAX_RETRIES = 2

def get_genai_model():
    """Lazy load GenAI to avoid import conflicts and configure it."""
    try:
        import google.generativeai as genai
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
        else:
            logger.warning("GEMINI_API_KEY is missing.")
        return genai.GenerativeModel(settings.LLM_MODEL)
    except ImportError:
        logger.error("google-generativeai package not found.")
        raise
    except Exception as e:
        logger.error(f"Failed to initialize GenAI: {e}")
        raise

def call_llm_with_schema(prompt: str, schema_path: str, timeout: int = 15) -> Dict[str, Any]:
    """
    Call LLM, extract first balanced JSON, validate against schema.
    """
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not configured.")

    try:
        model = get_genai_model()
    except Exception as e:
        raise RuntimeError(f"Model initialization failed: {e}")
    
    attempt = 0
    last_err = None
    
    while attempt <= MAX_RETRIES:
        attempt += 1
        try:
            logger.debug(f"LLM Call Attempt {attempt}/{MAX_RETRIES+1}")
            
            resp = model.generate_content(prompt)
            raw = resp.text
            
            # Parse
            try:
                obj = safe_load_json_from_text(raw)
                if not isinstance(obj, dict):
                    raise ValueError("LLM returned a list or primitive, expected JSON object.")
            except Exception as e:
                last_err = f"JSON parse error: {e}"
                logger.warning(f"LLM Response Parse Failed: {e}")
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
            logger.warning(f"LLM Schema Validation Failed: {err}")
            
        except Exception as e:
            last_err = f"LLM error: {str(e)}"
            logger.error(f"LLM error: {e}")
            
        time.sleep(1) # Backoff
        
    raise RuntimeError(f"LLM failed after {MAX_RETRIES+1} attempts. Last error: {last_err}")
