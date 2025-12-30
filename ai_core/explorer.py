import os
from typing import List, Dict, Any
from config import settings
from utils.ai_bridge import call_llm_with_schema

EXPLORATION_SCHEMA = settings.BASE_DIR / "schemas" / "exploration.schema.json"
PROJECTS_SCHEMA = settings.BASE_DIR / "schemas" / "projects.schema.json"

def suggest_exploration(skills: List[str], interests: List[str]) -> Dict[str, Any]:
    """
    Generates adjacent interests and opportunities.
    """
    prompt = f"""
    Act as a Career Strategy Genius.
    Maintain a strictly professional tone. DO NOT use emojis in the output.
    User Profile:
    - Current Skills: {', '.join(skills)}
    - Core Interests: {', '.join(interests)}
    
    1. Identify "Nearby Interests": Topics the user strictly DOES NOT have yet, but are logically the next step (e.g. Python -> Distributed Systems).
    2. Suggest "Opportunities": Generic types of real-world activities (e.g. "Contribute to LangChain", "Join Kaggle Titanics").
    
    Output JSON MUST match this structure exactly:
    {{
        "nearby_interests": [
            {{"name": "Topic", "description": "Why...", "relevance": "High"}}
        ],
        "opportunities": [
            {{"type": "Hackathon", "title": "Name of Event", "action": "Register and build..."}}
        ]
    }}
    """
    try:
        return call_llm_with_schema(prompt, str(EXPLORATION_SCHEMA))
    except Exception as e:
        return {"nearby_interests": [], "opportunities": [], "error": str(e)}

def generate_projects(skills: List[str], ambition: str) -> Dict[str, Any]:
    """
    Generates concrete project ideas to bridge the gap to ambition.
    """
    prompt = f"""
    Act as a Tech Lead.
    Maintain a strictly professional tone. DO NOT use emojis in the output.
    User Skills: {', '.join(skills)}
    Ambition: "{ambition}"
    
    Propose 3 High-Impact Portfolio Projects that:
    1. Utilize current skills.
    2. Force learning of NEW skills required for the Ambition.
    3. Are impressive on a resume (no To-Do lists).
    
    Output JSON MUST match this structure exactly:
    {{
        "projects": [
            {{
                "title": "Project Name",
                "tech_stack": ["Tool A", "Tool B"],
                "description": "What it does...",
                "difficulty": "Hard",
                "learning_outcome": "Mastery of X"
            }}
        ]
    }}
    """
    try:
        return call_llm_with_schema(prompt, str(PROJECTS_SCHEMA))
    except Exception as e:
        return {"projects": [], "error": str(e)}
