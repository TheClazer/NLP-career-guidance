"""
Confidence & Language Signal Analysis

Sentence-level linguistic classification with weighted scoring.
Outputs per-sentence trace for full explainability.
"""

import spacy
from typing import List, Dict, Tuple
import re

try:
    nlp = spacy.load("en_core_web_sm")
except:
    import en_core_web_sm
    nlp = en_core_web_sm.load()

# Action verbs (assertive language)
ACTION_VERBS = {
    "built", "designed", "implemented", "developed", "created", "architected",
    "deployed", "optimized", "led", "managed", "engineered", "achieved",
    "reduced", "increased", "improved", "delivered", "launched", "scaled"
}

# Hedging markers (uncertain language)
HEDGING_MARKERS = {
    "maybe", "kind of", "somewhat", "a bit", "possibly", "familiar with",
    "basic", "learning", "trying to", "hoping to", "interested in",
    "assisted", "helped", "involved in", "exposed to", "some experience"
}

# Passive voice patterns
PASSIVE_PATTERN = re.compile(r'\b(was|were|is|are|been|being)\s+\w+ed\b', re.I)


def analyze_hedging(text: str) -> Dict:
    """
    Analyze linguistic confidence using sentence-level classification.
    
    Formula: Confidence = (Action_Verbs * 1.5 - Hedge_Words) / Total_Sentences
    Normalized to [0, 1]
    
    Returns:
        {
            "score": float,          # Overall confidence [0-1]
            "markers": List[str],    # Found hedging markers
            "trace": List[Dict]      # Per-sentence analysis
        }
    """
    
    if not text:
        return {"score": 0.0, "markers": [], "trace": []}
    
    doc = nlp(text)
    sentences = list(doc.sents)
    
    if not sentences:
        return {"score": 0.0, "markers": [], "trace": []}
    
    trace = []
    total_action_score = 0
    total_hedge_penalty = 0
    found_markers = set()
    
    for sent in sentences:
        sent_text = sent.text.strip()
        sent_lower = sent_text.lower()
        
        # Count action verbs
        action_count = sum(1 for token in sent if token.lemma_.lower() in ACTION_VERBS)
        
        # Count hedging markers
        hedge_count = sum(1 for marker in HEDGING_MARKERS if marker in sent_lower)
        
        # Check for passive voice
        has_passive = bool(PASSIVE_PATTERN.search(sent_text))
        
        # Classify sentence
        if action_count >= 2:
            classification = "assertive"
            sentence_score = 1.5
        elif action_count == 1 and hedge_count == 0:
            classification = "neutral"
            sentence_score = 0.5
        elif hedge_count > 0:
            classification = "hedged"
            sentence_score = -1.0
            # Track specific markers
            for marker in HEDGING_MARKERS:
                if marker in sent_lower:
                    found_markers.add(marker)
        else:
            classification = "neutral"
            sentence_score = 0.5
        
        # Passive voice penalty
        if has_passive:
            sentence_score -= 0.3
        
        total_action_score += max(0, sentence_score)
        total_hedge_penalty += max(0, -sentence_score)
        
        trace.append({
            "sentence": sent_text[:100] + "..." if len(sent_text) > 100 else sent_text,
            "classification": classification,
            "action_verbs": action_count,
            "hedge_markers": hedge_count,
            "has_passive": has_passive,
            "score": sentence_score
        })
    
    # Compute final confidence score
    raw_score = (total_action_score - total_hedge_penalty) / len(sentences)
    
    # Normalize to [0, 1] - assuming typical range is [-1, 1.5]
    normalized_score = max(0.0, min(1.0, (raw_score + 1.0) / 2.5))
    
    return {
        "score": round(normalized_score, 3),
        "markers": sorted(list(found_markers)),
        "trace": trace
    }


def confidence_score(text: str) -> float:
    """
    Backward-compatible wrapper returning just the score.
    """
    result = analyze_hedging(text)
    return result["score"]
