import sys
import os
import json
import traceback

# 1. Setup Environment
print("--- [1] Environment Setup ---")
from config import settings
from utils.logging_config import logger
print(f"Loaded Config: {settings.APP_NAME}")
print(f"API Key Present: {bool(settings.GEMINI_API_KEY)}")

# 2. Import Modules
print("\n--- [2] Module Imports ---")
try:
    print("Importing NLP Engine...")
    from nlp.nlp_engine import analyze_text
    print("✓ NLP Engine Imported")
    
    print("Importing Intelligence (Ontology)...")
    from intelligence.ontology import normalize_skills, DATA_PATH as ONTOLOGY_PATH
    print("✓ Ontology Imported")
    
    print("Importing Intelligence (Role Matcher)...")
    from intelligence.role_matcher import calculate_role_fit
    print("✓ Role Matcher Imported")
    
except Exception as e:
    print(f"❌ FATAL IMPORT ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)

# 3. Execution Test
print("\n--- [3] Execution Test ---")
SAMPLE_RESUME = """
Summary: Senior Python Developer with 5 years experience in Django and AWS.
"""
KEYWORDS = ["Python", "Django", "AWS", "Docker"]

try:
    print("Running NLP Analysis...")
    signals = analyze_text(SAMPLE_RESUME, KEYWORDS)
    print(f"✓ Skills Found: {[s.get('skill', s.get('name')) for s in signals['skills']]}")
    
    print("Running Skill Normalization...")
    # This triggers the lazy import of gemini_client
    norm = normalize_skills(signals["skills"])
    print(f"✓ Normalized: {[s.get('name', s.get('skill', '')) if isinstance(s, dict) else s for s in norm]}")
    
    print("Running Role Matching...")
    norm_skills_list = [s.get('name', s.get('skill', '')) if isinstance(s, dict) else s for s in norm]
    role_fit = calculate_role_fit(norm_skills_list, "Backend Developer", signals["confidence_score"])
    print(f"✓ Role Fit Score: {role_fit.get('score')}")
    
except Exception as e:
    print(f"❌ EXECUTION ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n--- SYSTEM VERIFIED GREEN ---")
