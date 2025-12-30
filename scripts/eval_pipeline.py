import json
import sys
import os

# Add parent directory to path so imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nlp.nlp_engine import analyze_text
# We need keywords to force extraction since our extractor depends on them?
# extract_skills_with_evidence requires keywords.
# In app.py we load them from ontology. We must do same here.
from intelligence.ontology import normalize_skills, DATA_PATH as ONTOLOGY_PATH

def run_eval():
    # Load canned profiles
    with open("data/demo_profiles.json", "r") as f:
        profiles = json.load(f)
        
    with open(ONTOLOGY_PATH, "r") as f:
        ontology = json.load(f)
    keywords = list(ontology.keys())
    
    total_profiles = len(profiles)
    passed_profiles = 0
    
    print(f"📉 Starting Evaluation on {total_profiles} profiles...\n")
    
    for p in profiles:
        print(f"Analyzing profile: {p['id']}...")
        result = analyze_text(p['text'], keywords)
        
        # result['skills'] is List[Dict] e.g. [{'name': 'python', 'evidence': ...}]
        extracted = set([s['name'].lower() for s in result['skills']])
        expected = set([s.lower() for s in p['expected_skills']])
        
        # Calculate Recall (How many expected skills did we find?)
        intersection = extracted.intersection(expected)
        recall = len(intersection) / len(expected) if len(expected) > 0 else 0
        
        print(f"  - Recall: {recall:.2f}")
        
        if recall >= 0.5:
            passed_profiles += 1
            
    print(f"\n✅ Evaluation Complete. Pass Rate: {passed_profiles}/{total_profiles}")

if __name__ == "__main__":
    run_eval()
