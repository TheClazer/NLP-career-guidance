import os
from google.generativeai import GenerativeModel
from config import settings

def call_small_llm_text(prompt: str, timeout=10):
    """
    Simple text-only LLM call for non-critical heuristic tasks like bullet optimization.
    """
    try:
        model = GenerativeModel(settings.LLM_MODEL)
        resp = model.generate_content(prompt)
        return resp.text.strip()
    except Exception as e:
        return f"Optimization unavailable: {str(e)}"
