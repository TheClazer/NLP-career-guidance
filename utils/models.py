from pydantic import BaseModel, Field
from typing import List, Optional

class UserProfile(BaseModel):
    """
    Unified profile model for both Resume-based and Manual entries.
    """
    is_manual: bool = False
    name: str = "Candidate"
    
    # Core Data
    raw_text: str = "" # Resume text or concatenated manual input
    skills: List[str] = Field(default_factory=list)
    
    # Strategic Data (Manual)
    interests: List[str] = Field(default_factory=list)
    current_role: str = "Explorer"
    target_role: str = "Undecided" 
    ambition: str = "" # "Become a CTO", "Build a startup"
    
    # Analysis Results (Populated later)
    confidence_score: float = 0.0
