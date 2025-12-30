import os
import json
from utils.ai_bridge import call_llm_with_schema
from config import settings
from pathlib import Path

SCHEMA_PATH = settings.BASE_DIR / "schemas" / "roadmap.schema.json"

def generate_roadmap(role, missing_skills, time_commitment):
    """
    Generates a structured career roadmap using the hardened LLM client.
    Returns: Dict (Structured Roadmap) or error dict fallback.
    """
    prompt = f"""
    Act as a Senior Technical Career Coach.
    Maintain a strictly professional tone. DO NOT use emojis in the output.
    Create a step-by-step learning roadmap for the role: '{role}'.
    The candidate matches most skills but is MISSING: {', '.join(missing_skills)}.
    Available Time: {time_commitment}.
    
    Structure the roadmap into 3 distinct phases (e.g. Month 1, Month 2, Month 3).
    Focus specifically on the MISSING skills.
    
    Output STRICT JSON:
    {{
      "role": "{role}",
      "phases": [
         {{ "phase_name": "Phase 1: Foundations", "duration": "Week 1-4", "topics": ["Topic A", "Topic B"] }}
      ]
    }}
    """
    
    try:
        return call_llm_with_schema(prompt, SCHEMA_PATH)
    except Exception as e:
        return {
            "role": role,
            "phases": [
                {
                    "phase_name": "Emergency Recovery Plan",
                    "duration": "Immediate",
                    "topics": [f"Focus on: {', '.join(missing_skills)}", "Consult official documentation"]
                }
            ],
            "error": str(e)
        }
