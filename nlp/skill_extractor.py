"""
Deterministic Semantic Skill Extractor

Three-layer architecture:
1. Linguistic Candidate Extraction (spaCy)
2. Negation & Context Filtering
3. Semantic Normalization (Embeddings)

Output: Structured skill objects with full explainability
"""

import spacy
from typing import List, Dict
from functools import lru_cache
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging

logger = logging.getLogger(__name__)

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    import en_core_web_sm
    nlp = en_core_web_sm.load()

# Embedding model (cached)
@lru_cache(maxsize=1)
def get_embedding_model():
    """Load sentence transformer model (cached)"""
    return SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Action verbs that indicate skill usage
ACTION_VERBS = {
    "built", "designed", "implemented", "developed", "created", "architected",
    "deployed", "optimized", "led", "managed", "engineered", "coded", "wrote",
    "maintained", "refactored", "automated", "integrated", "scaled"
}

# Stop phrases to ignore
STOP_PHRASES = {
    "interested in", "learning", "want to learn", "familiar with",
    "looking to", "hoping to", "planning to"
}

# Negation markers
NEGATION_DEPS = {"neg", "not"}
NEGATION_TOKENS = {"no", "not", "never", "n't", "without", "lack"}

def extract_skills_with_evidence(text: str, ontology_skills: List[str]) -> List[Dict]:
    """
    Extract skills using three-layer semantic approach.
    
    Args:
        text: Resume or profile text
        ontology_skills: Canonical skill names from ontology
        
    Returns:
        List of skill objects: {skill, confidence, evidence, depth}
    """
    
    if not text or not ontology_skills:
        return []
    
    doc = nlp(text)
    
    # LAYER 1: Linguistic Candidate Extraction
    candidates = _extract_candidates(doc)
    
    # LAYER 2: Negation & Context Filtering
    candidates = _filter_negations(candidates, doc)
    
    # LAYER 3: Semantic Normalization
    skills = _semantic_matching(candidates, ontology_skills)
    
    return skills


def _extract_candidates(doc) -> List[Dict]:
    """
    Layer 1: Extract skill candidates from text using linguistic patterns.
    
    Returns list of candidates with evidence sentences.
    """
    candidates = []
    
    for sent in doc.sents:
        sent_text = sent.text.strip()
        
        # Check if sentence has action verbs
        has_action = any(token.lemma_.lower() in ACTION_VERBS for token in sent)
        
        # Check for stop phrases
        has_stop_phrase = any(phrase in sent_text.lower() for phrase in STOP_PHRASES)
        
        if has_stop_phrase:
            continue
            
        # Extract noun chunks as candidates
        for chunk in sent.noun_chunks:
            chunk_text = chunk.text.strip()
            
            # Skip very short or very long chunks
            if len(chunk_text) < 2 or len(chunk_text) > 50:
                continue
                
            # Determine depth based on context
            depth = "applied" if has_action else "mentioned"
            
            candidates.append({
                "text": chunk_text,
                "sentence": sent_text,
                "depth": depth,
                "span": chunk
            })
    
    return candidates


def _filter_negations(candidates: List[Dict], doc) -> List[Dict]:
    """
    Layer 2: Filter out candidates that are negated or in negative context.
    
    Examples to reject:
    - "No experience in Java"
    - "I have not used Python"
    - "Never worked with databases"
    """
    filtered = []
    
    for cand in candidates:
        span = cand["span"]
        is_negated = False
        
        # Check for negation dependencies
        for token in span:
            # Check if token has negation dependency
            if any(dep.lower() in NEGATION_DEPS for dep in [token.dep_]):
                is_negated = True
                break
                
            # Check if governed by negation token
            if token.head.text.lower() in NEGATION_TOKENS:
                is_negated = True
                break
        
        # Check sentence-level negation phrases
        sent_lower = cand["sentence"].lower()
        if any(phrase in sent_lower for phrase in ["no experience", "have not", "never worked", "not familiar"]):
            is_negated = True
        
        if not is_negated:
            filtered.append(cand)
        else:
            logger.debug(f"Filtered negated candidate: {cand['text']}")
    
    return filtered


@lru_cache(maxsize=512)
def _get_ontology_embeddings(ontology_tuple):
    """Cache embeddings for ontology skills"""
    model = get_embedding_model()
    return model.encode(list(ontology_tuple))


def _semantic_matching(candidates: List[Dict], ontology_skills: List[str], threshold: float = 0.75) -> List[Dict]:
    """
    Layer 3: Match candidates to canonical ontology skills using semantic similarity.
    
    Args:
        candidates: Filtered candidate phrases
        ontology_skills: Canonical skill names
        threshold: Minimum cosine similarity for match (0.75)
        
    Returns:
        Structured skill objects with confidence scores
    """
    
    if not candidates or not ontology_skills:
        return []
    
    model = get_embedding_model()
    
    # Get embeddings (cached)
    ontology_tuple = tuple(sorted(ontology_skills))
    ontology_embeddings = _get_ontology_embeddings(ontology_tuple)
    
    # Group candidates by text to deduplicate
    skill_dict = {}
    
    for cand in candidates:
        cand_text = cand["text"]
        
        # Embed candidate
        cand_embedding = model.encode([cand_text])
        
        # Compute similarities
        similarities = cosine_similarity(cand_embedding, ontology_embeddings)[0]
        max_idx = np.argmax(similarities)
        max_sim = similarities[max_idx]
        
        if max_sim >= threshold:
            matched_skill = ontology_skills[max_idx]
            
            # Aggregate evidence
            if matched_skill not in skill_dict:
                skill_dict[matched_skill] = {
                    "skill": matched_skill,
                    "confidence": float(max_sim),
                    "evidence": [],
                    "depth": cand["depth"]
                }
            
            # Add evidence sentence if not duplicate
            if cand["sentence"] not in skill_dict[matched_skill]["evidence"]:
                skill_dict[matched_skill]["evidence"].append(cand["sentence"])
            
            # Update depth if more specific
            if cand["depth"] == "applied" and skill_dict[matched_skill]["depth"] == "mentioned":
                skill_dict[matched_skill]["depth"] = "applied"
    
    return list(skill_dict.values())
