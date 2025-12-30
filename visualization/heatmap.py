import re
from typing import List

def render_resume_heatmap(text: str, detected_skills: List[str]):
    """
    Annotates the resume text with HTML highlighting.
    - Power Words / Skills -> Green
    - Weak Words / Fluff -> Red
    """
    
    # Simple list for MVP V2
    POWER_WORDS = [
        "architected", "deployed", "optimized", "scaled", "led", "engineered", 
        "implemented", "developed", "created", "managed", "orchestrated", "refactored"
    ]
    
    FLUFF_WORDS = [
        "motivated", "team player", "hard worker", "passionate", "various", 
        "responsible for", "helped", "assisted", "familiar with"
    ]
    
    # Escape text for HTML
    annotated = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    
    # Highlight Skills (Blue)
    for skill in detected_skills:
        # Case insensitive replacement preserving case
        pattern = re.compile(re.escape(skill), re.IGNORECASE)
        annotated = pattern.sub(f'<span style="background-color: rgba(0, 114, 255, 0.2); border-bottom: 2px solid #0072FF; padding: 0 4px; border-radius: 4px;">{skill}</span>', annotated)

    # Highlight Power Words (Green)
    for word in POWER_WORDS:
        pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
        annotated = pattern.sub(f'<span style="background-color: rgba(0, 255, 136, 0.2); color: #00FF88; font-weight: bold;">{word}</span>', annotated)

    # Highlight Fluff (Red)
    for word in FLUFF_WORDS:
        pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
        annotated = pattern.sub(f'<span style="background-color: rgba(255, 50, 50, 0.2); color: #FF3232; text-decoration: line-through;">{word}</span>', annotated)
    
    return f"""
    <div style="
        font-family: 'Courier New', monospace; 
        white-space: pre-wrap; 
        background: rgba(255,255,255,0.05); 
        padding: 20px; 
        border-radius: 12px; 
        font-size: 14px; 
        line-height: 1.6;
        color: #ddd;
        border: 1px solid rgba(255,255,255,0.1);
    ">
    {annotated}
    </div>
    """
