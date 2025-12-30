import json
from typing import List, Dict, Union, Any, Optional
# from llm.gemini_client import call_llm_with_schema (Moved to function scope)
from config import settings
from utils.logging_config import logger

# Load Canonical Ontology
DATA_PATH = settings.DATA_DIR / "skill_ontology.json"
try:
    with open(DATA_PATH, "r", encoding='utf-8') as f:
        ONTOLOGY: Dict[str, str] = json.load(f)
except FileNotFoundError:
    logger.warning("skill_ontology.json not found in data directory. Initializing empty ontology.")
    ONTOLOGY = {}
except json.JSONDecodeError as e:
    logger.error(f"Failed to parse skill_ontology.json: {e}")
    ONTOLOGY = {}

# Session Cache
SESSION_CACHE: Dict[str, str] = {}

SCHEMA_PATH = settings.SCHEMA_DIR / "normalization.schema.json"

def normalize_skill_hybrid(raw_skill: str) -> str:
    """
    Hybrid normalization: Tier 1 (Lookup), Tier 2 (Cache), Tier 3 (LLM Client)
    """
    if not raw_skill:
        return ""

    raw_lower = raw_skill.lower()
    
    if raw_lower in ONTOLOGY:
        return ONTOLOGY[raw_lower]
    
    if raw_lower in SESSION_CACHE:
        return SESSION_CACHE[raw_lower]

    try:
        from utils.ai_bridge import call_llm_with_schema
        prompt = f"""
        Normalize this skill term: '{raw_skill}' to a standard canonical name.
        Example: "React.js 18" -> "React"
        
        Output JSON:
        {{ "normalized_name": "React" }}
        """
        
        # Ensure schema path is string for compatibility if needed, though pathlib is usually fine
        data = call_llm_with_schema(prompt, str(SCHEMA_PATH))
        normalized = data.get("normalized_name", raw_skill.title())
        
        SESSION_CACHE[raw_lower] = normalized
        return normalized
    except Exception as e:
        logger.error(f"LLM Normalization failed for '{raw_skill}': {e}")
        # Fallback
        return raw_skill.title()

def normalize_skills(raw_skills_input: Union[List[str], List[Dict[str, Any]]]) -> List[Any]:
    """
    Normalizes a list of skills (strings or dicts).
    """
    if not raw_skills_input:
        return []
    
    first_item = raw_skills_input[0]
    
    if isinstance(first_item, str):
        normalized_set = set()
        for skill in raw_skills_input:
            if isinstance(skill, str): # Mypy safety
                norm = normalize_skill_hybrid(skill)
                normalized_set.add(norm)
        return list(normalized_set)
        
    elif isinstance(first_item, dict):
        normalized_map = {}
        for item in raw_skills_input: # type: ignore
             if isinstance(item, dict):
                raw_name = item.get("skill", item.get("name", ""))
                norm_name = normalize_skill_hybrid(raw_name)
                if norm_name not in normalized_map:
                    new_item = item.copy()
                    new_item["name"] = norm_name
                    normalized_map[norm_name] = new_item
        return list(normalized_map.values())
        
    return []
