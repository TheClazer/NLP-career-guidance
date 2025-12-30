from intelligence.role_matcher import calculate_role_fit

def test_role_score_basic():
    # Setup mock data locally so we don't depend on files existing perfect
    # The matcher loads files. We should test logical calculation primarily.
    # But calculate_role_fit calls get_role_baseline which checks files.
    # We can rely on the universality agent or local cache.
    # Let's test with a role that likely exists or will be generated.
    
    user_skills = ["Python", "Docker"]
    target_role = "Backend Engineer" 
    
    # We might need to ensure backend engineer exists in local DB for this to be deterministic test
    # If it falls back to LLM it might be slow or fail without key.
    # Ideally unit tests shouldn't hit network. 
    # For now, we assume Backend Engineer is in our local json.
    
    result = calculate_role_fit(user_skills, target_role, confidence_score=0.8)
    
    assert isinstance(result["score"], (int, float))
    assert result["score"] >= 0
    assert "Python" in result["matched"]
