from typing import List, Dict
import re

# Minimal heuristic scoring for MVP
WEIGHT_SKILL = 0.5
WEIGHT_IMPACT = 0.3
WEIGHT_CLARITY = 0.2

IMPACT_KEYWORDS = ["improved", "reduced", "increased", "%", "by", "from", "to", "resulted"]
METRIC_RE = re.compile(r'\b\d+%|\b\d+\s+(?:hours|days|users|clients|transactions)\b', re.I)

def score_resume_text(text: str, detected_skills: List[str], readability_score: float) -> Dict:
    """
    Returns score (0-100), breakdown, and suggestions.
    """
    # 8 skills -> full marks
    skill_score = min(len(set(detected_skills)) / 8.0, 1.0)  
    
    impact_count = len(METRIC_RE.findall(text)) + sum(1 for k in IMPACT_KEYWORDS if k in text.lower())
    impact_score = min(impact_count / 4.0, 1.0)
    
    # Heuristic: lower grade -> simpler/better clarity
    clarity_score = max(0.0, min(1.0, (16.0 - readability_score) / 10.0))  

    total = (skill_score * WEIGHT_SKILL) + (impact_score * WEIGHT_IMPACT) + (clarity_score * WEIGHT_CLARITY)
    
    return {
        "score": int(total * 100),
        "breakdown": {
            "skill_score": round(skill_score * 100, 1),
            "impact_score": round(impact_score * 100, 1),
            "clarity_score": round(clarity_score * 100, 1)
        },
        "tips": generate_tips(text, detected_skills)
    }

def generate_tips(text: str, detected_skills: List[str]):
    tips = []
    # Tip: add metrics if none
    if len(METRIC_RE.findall(text)) == 0:
        tips.append("Add measurable outcomes (numbers, percentages) for your major bullets.")
    
    # Tip: tense and action verbs
    if "responsible for" in text.lower():
        tips.append("Prefer active bullets using strong verbs (e.g., 'Built', 'Improved', 'Reduced').")
    
    # Tip: skill coverage
    if len(detected_skills) < 4:
        tips.append("Mention more concrete skills or tools (include frameworks, databases, libraries).")
        
    return tips
