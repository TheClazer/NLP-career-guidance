import re

def calculate_ats_score(text: str) -> dict:
    """
    Analyzes text for ATS (Applicant Tracking System) parsability errors.
    Returns a score (0-100) and a list of issues.
    """
    if not text:
        return {"score": 0, "issues": ["No text provided"]}
        
    issues = []
    score = 100
    
    # 1. Whitespace Ratio (Detect bad extracting from PDFs)
    # Good text should be mostly characters, but not solid blocks.
    # We look for extreme density or lack thereof.
    # Actually, a common issue is too many special characters vs text.
    
    char_count = len(text)
    special_chars = len(re.findall(r'[^a-zA-Z0-9\s]', text))
    special_char_ratio = special_chars / char_count if char_count > 0 else 0
    
    if special_char_ratio > 0.15: # Arbitrary threshold for "messy" text
        score -= 20
        issues.append("High density of special characters (Formatting issues?)")
        
    # 2. Sentence Length / Structure
    sentences = text.split('.')
    avg_len = sum(len(s.split()) for s in sentences) / max(1, len(sentences))
    
    if avg_len < 5:
        score -= 10
        issues.append("Sentences are too short/fragmented (Bullet point parsing issue?)")
    elif avg_len > 40:
        score -= 10
        issues.append("Sentences are too long (Run-on text)")
        
    # 3. Email/Phone presence (Should be there for a resume, usually)
    # Using simple regex checks
    has_email = bool(re.search(r'\S+@\S+', text))
    has_phone = bool(re.search(r'\d[\d -]{8,12}\d', text))
    
    if not has_email and not has_phone:
        # Not strictly a formatting error, but an ATS warning
        # We won't penalize score heavily, just warn
        issues.append("Contact info might be missing or unparsable")
        
    # 4. Text Length
    word_count = len(text.split())
    if word_count < 50:
        score -= 30
        issues.append("Text too short to analyze effectively")
        
    return {
        "score": max(0, round(score)),
        "issues": issues
    }
