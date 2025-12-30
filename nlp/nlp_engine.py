from typing import Dict, List, Optional, Any
import logging

from nlp.preprocess import clean_text, tokenize_sentences
from nlp.skill_extractor import extract_skills_with_evidence
from nlp.confidence import analyze_hedging
from nlp.readability import readability_score
from nlp.ats_check import calculate_ats_score
from utils.logging_config import logger

def analyze_text(text: str, skill_keywords: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Orchestrates the NLP analysis pipeline.
    
    Args:
        text (str): The raw input text (e.g., from a resume).
        skill_keywords (List[str], optional): List of knowledge base skills for matching.
        
    Returns:
        Dict[str, Any]: A dictionary containing analysis results including skills, confidence, hedging, and ATS checks.
    """
    if not text:
        logger.warning("Empty text provided to analyze_text")
        return {
            "skills": [],
            "skills_raw": [],
            "sentences": [],
            "confidence_score": 0.0,
            "confidence_trace": [],
            "hedging_markers": [],
            "readability": 0.0,
            "ats_result": {"score": 0, "issues": []}
        }
    
    try:
        # 1. Cleaning & Preprocessing
        cleaned_text = clean_text(text)
        sentences = tokenize_sentences(text)  # Use spaCy tokenizer for robustness
        
        # 2. Skill Extraction
        safe_keywords = skill_keywords if skill_keywords else []
        skills_data = extract_skills_with_evidence(cleaned_text, safe_keywords)
        
        # 3. Confidence Analysis (Hedging)
        # Note: analyze_hedging likely works on sentences or full text. Passing cleaned_text.
        hedging_result = analyze_hedging(cleaned_text)
        
        # 4. Readability Analysis
        readability = readability_score(cleaned_text)
        
        # 5. ATS Compliance Check
        # IMPORTANT: ATS check requires raw text to detect contact info formatting issues that might be stripped by cleaning.
        ats_result = calculate_ats_score(text)
        
        logger.info(f"Analysis complete. Found {len(skills_data)} skills.")
        
        return {
            "skills": skills_data,
            "skills_raw": [s.get("skill", s.get("name")) for s in skills_data],
            "sentences": sentences,
            "confidence_score": hedging_result.get("score", 0.0),
            "confidence_trace": hedging_result.get("trace", []),
            "hedging_markers": hedging_result.get("markers", []),
            "readability": readability,
            "ats_result": ats_result
        }

    except Exception as e:
        logger.exception("Critical failure in NLP analysis pipeline")
        # Return a safe fallback structure to prevent app crash
        return {
            "error": str(e),
            "skills": [],
            "skills_raw": [],
            "confidence_score": 0.0,
            "readability": 0.0,
            "ats_result": {}
        }
