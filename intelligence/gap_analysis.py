def gap_analysis(user_skills_input, role_requirements_input):
    """
    Identifies missing skills.
    user_skills_input: List[str] or List[Dict]
    role_requirements_input: List[str] or Dict[str, int]
    """
    # 1. Normalize User Skills to Set[str]
    user_lower = set()
    if user_skills_input:
        first = user_skills_input[0]
        if isinstance(first, dict):
            user_lower = {s["name"].lower() for s in user_skills_input}
        else:
            user_lower = {s.lower() for s in user_skills_input}
            
    # 2. Extract Role Skills
    role_skills_map = {} # lower -> original
    
    if isinstance(role_requirements_input, list):
        for s in role_requirements_input:
            role_skills_map[s.lower()] = s
    elif isinstance(role_requirements_input, dict):
        for s in role_requirements_input.keys():
            role_skills_map[s.lower()] = s
            
    # 3. Find Missing
    missing = []
    for s_lower, s_original in role_skills_map.items():
        if s_lower not in user_lower:
            missing.append(s_original)
            
    return missing
