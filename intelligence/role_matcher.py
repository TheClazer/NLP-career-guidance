"""
Deterministic Role Matching with Full Score Decomposition

All weights loaded from role_baselines.json.
Outputs complete score breakdown for viva defense.
"""

import json
from typing import Dict, List, Any
# from llm.gemini_client import call_llm_with_schema
from intelligence.sanity import sanity_check_role_baseline
from config import settings
from utils.logging_config import logger

# Load local cache
try:
    with open(settings.DATA_DIR / "role_baselines.json", "r", encoding='utf-8') as f:
        LOCAL_ROLES: Dict[str, Dict] = json.load(f)
except FileNotFoundError:
    logger.warning("role_baselines.json not found. Role matching will rely on LLM fallback.")
    LOCAL_ROLES = {}
except json.JSONDecodeError as e:
    logger.error(f"Failed to parse role_baselines.json: {e}")
    LOCAL_ROLES = {}

SCHEMA_PATH = settings.SCHEMA_DIR / "role_baseline.schema.json"


def get_role_baseline(target_role: str) -> Dict[str, Any]:
    """
    Hybrid logic: Check local DB first, then generate via LLM if missing.
    
    Returns standardized baseline with core/secondary/optional skills.
    """
    # Local DB lookup
    if target_role in LOCAL_ROLES:
        return {**LOCAL_ROLES[target_role], "source": "local"}
    
    # Agentic generation
    return generate_dynamic_baseline(target_role)


def generate_dynamic_baseline(role: str) -> Dict[str, Any]:
    """
    Generate baseline via LLM with schema validation.
    """
    prompt = f"""
    Act as a Global Career Architect.
    Create a 2025 Skill Baseline for: '{role}'.
    
    Output STRICT JSON:
    {{
      "core_skills": ["Skill A", "Skill B"],
      "secondary_skills": ["Skill C"],
      "optional_skills": ["Skill D"],
      "weights": {{"Skill A": 5, "Skill B": 4, "Skill C": 3, "Skill D": 2}},
      "core_penalty": 0.3
    }}
    """
    
    try:
        from utils.ai_bridge import call_llm_with_schema
        data = call_llm_with_schema(prompt, str(SCHEMA_PATH))
        is_valid, err = sanity_check_role_baseline(data)
        if not is_valid:
            raise ValueError(err)
        data["source"] = "heuristic"
        return data
    except Exception as e:
        logger.error(f"Role baseline generation failed for '{role}': {e}")
        # Fallback
        return {
            "core_skills": ["Communication", "Problem Solving"],
            "secondary_skills": ["Teamwork"],
            "optional_skills": [],
            "weights": {"Communication": 5, "Problem Solving": 5, "Teamwork": 3},
            "core_penalty": 0.2,
            "source": "fallback"
        }


def calculate_role_fit(user_skills: List[str], target_role: str, confidence_score: float) -> Dict[str, Any]:
    """
    Compute role fit with full score decomposition.
    
    Returns:
        Dict: Fit analysis with scores, matched lists, and breakdown.
    """
    if not target_role:
        logger.warning("No target role provided for calculation.")
        return {}

    baseline = get_role_baseline(target_role)
    
    user_skills_set = set(s.lower() for s in user_skills)
    
    # Extract skill tiers
    core_skills = set(s.lower() for s in baseline.get("core_skills", []))
    secondary_skills = set(s.lower() for s in baseline.get("secondary_skills", []))
    optional_skills = set(s.lower() for s in baseline.get("optional_skills", []))
    
    all_skills = core_skills | secondary_skills | optional_skills
    weights = {k.lower(): v for k, v in baseline.get("weights", {}).items()}
    core_penalty_coeff = baseline.get("core_penalty", 0.3)
    
    # Compute matches
    matched_core = core_skills & user_skills_set
    matched_secondary = secondary_skills & user_skills_set
    matched_optional = optional_skills & user_skills_set
    
    missing_core = core_skills - user_skills_set
    missing_secondary = secondary_skills - user_skills_set
    
    # Weighted scoring
    total_weight = sum(weights.values())
    earned_weight = sum(weights.get(skill, 0) for skill in user_skills_set if skill in weights)
    
    skill_score = (earned_weight / total_weight) if total_weight > 0 else 0
    
    # Core skill penalty
    penalties = []
    if missing_core:
        penalty = len(missing_core) * core_penalty_coeff
        skill_score = max(0, skill_score - penalty)
        penalties.append(f"Missing {len(missing_core)} core skills: {', '.join(list(missing_core)[:3])}")
    
    # Final formula: 70% skill, 30% confidence
    # Final formula: 70% skill, 30% confidence (normalized from 0-10 to 0-1)
    final_score = (skill_score * 0.7) + ((confidence_score / 10.0) * 0.3)
    
    # Prepare matched/missing lists (original case) using intersection logic against original user input might be better?
    # but for now, returning matched strings is fine.
    
    matched = []
    # Identify which original user skills matched anything
    # This is O(N*M) but N is small.
    # To keep original casing:
    flat_matched = matched_core | matched_secondary | matched_optional
    for skill in user_skills:
        if skill.lower() in flat_matched:
            matched.append(skill)
    
    missing = list(missing_core) + list(missing_secondary)
    
    return {
        "score": round(final_score * 100, 1),
        "skill_score": round(skill_score * 100, 1),
        "language_score": round(confidence_score * 100, 1),
        "matched": matched,
        "missing": missing,
        "penalties": penalties,
        "breakdown": {
            "core_matched": len(matched_core),
            "core_total": len(core_skills),
            "secondary_matched": len(matched_secondary),
            "secondary_total": len(secondary_skills),
            "optional_matched": len(matched_optional),
            "earned_weight": earned_weight,
            "total_weight": total_weight
        },
        "baseline": baseline
    }
