import numpy as np
from typing import List, Dict, Any, Tuple
from collections import Counter
from utils.logging_config import logger

def calculate_skill_vector(user_skills: List[str], role_baselines: Dict[str, Any]) -> Dict[str, float]:
    """
    Converts skill lists into a vector space to calculate semantic distance.
    Returns quantitative metrics for radar charts.
    """
    # Categories of skills (simplified ontology mapping for V2)
    # in V3 this should come from the ontology file directly
    AXES = {
        "Technical": ["python", "java", "sql", "aws", "docker", "kubernetes", "react", "node", "django", "fastapi"],
        "Data": ["pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "tableau", "power bi"],
        "Leadership": ["agile", "scrum", "leadership", "management", "mentoring", "strategy"],
        "Soft Skills": ["communication", "teamwork", "problem solving", "critical thinking", "negotiation"],
        "Operational": ["jira", "git", "ci/cd", "jenkins", "terraform", "linux"]
    }
    
    # Normalize user skills
    user_set = {s.lower() for s in user_skills}
    
    scores = {}
    
    for axis, keywords in AXES.items():
        # Calculate coverage: How many keywords in this axis does the user have?
        # This is a heuristic proxy for "strength" in that dimension
        # In a real vector model, we'd use cosine similarity of embeddings. 
        # For V2 MVP, we use Keyword Coverage Ratio (KCR).
        
        matches = sum(1 for k in keywords if k in user_set)
        total = len(keywords)
        
        # Scaling score 0-100, but ensuring it's not too harsh
        # If you have 3/10 technical skills, that's decent. 5/10 is senior.
        raw_score = (matches / total) * 100
        
        # Sigmoid-like boost: small matches count for more
        # 1 match = ~20%, 3 matches = ~60%, 5 matches = 90%
        # Simple heuristic limit
        scores[axis] = min(round(raw_score * 2.5, 1), 100.0)

    return scores

def compare_vectors(user_vector: Dict[str, float], role_vector: Dict[str, float]) -> Dict[str, Any]:
    """
    Compares two vectors to find the 'Gap Area'.
    """
    gaps = {}
    for axis, u_score in user_vector.items():
        r_score = role_vector.get(axis, 50.0) # Default expectation
        gaps[axis] = r_score - u_score
    
    return {
        "user_vector": user_vector,
        "role_vector": role_vector,
        "gaps": gaps
    }
