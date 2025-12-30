from intelligence.role_matcher import  get_role_baseline
from typing import List, Dict

# Heuristic function to find simplified role fit without full weight calc if needed, 
# or we can reuse role_matcher logic but we need to inverse it (find roles for skills).
# Since role_matcher computes fit GIVEN a role, we might need a new approach or iterate all roles.
# For MVP, we will iterate all local roles in role_baselines.

def get_target_roles(user_skills: List[str], roles_db: Dict, target_role: str=None, top_n:int=3) -> List[str]:
    """
    Returns a list of target roles. If target_role is provided, returns [target_role].
    Otherwise, scans roles_db to find best overlaps with user_skills.
    """
    if target_role:
        return [target_role]
    
    # scan local db
    scores = []
    user_skills_set = set(s.lower() for s in user_skills)
    
    for r, data in roles_db.items():
        # Quick overlap check
        # Quick overlap check
        # Support new schema (core_skills) and old schema (required_skills)
        req = set()
        if "required_skills" in data:
            req.update(s.lower() for s in data["required_skills"])
        if "core_skills" in data:
            req.update(s.lower() for s in data["core_skills"])
        if "secondary_skills" in data:
            req.update(s.lower() for s in data["secondary_skills"])
        if "weights" in data:
            req.update(s.lower() for s in data["weights"].keys())
            
        if not req:
            continue
        overlap = len(user_skills_set.intersection(req))
        score = overlap / len(req)
        scores.append((r, score))
        
    sorted_roles = sorted(scores, key=lambda x: x[1], reverse=True)
    return [r for r, s in sorted_roles[:top_n]]


def aggregate_role_skills(role_list: List[str], roles_db:Dict) -> List[str]:
    # roles_db is role_baselines dict
    agg = []
    for r in role_list:
        # We need to handle the structure of roles_db (see role_baselines.json)
        # It might use 'required_skills' or keys of 'weights'
        data = roles_db.get(r, {})
        rs = []
        if "required_skills" in data:
            rs.extend(data["required_skills"])
        if "core_skills" in data:
            rs.extend(data["core_skills"])
        if "secondary_skills" in data:
            rs.extend(data["secondary_skills"])
        if "weights" in data:
            rs.extend(list(data["weights"].keys()))
        agg.extend(rs)
        
    # dedupe preserving simple order
    seen=set(); out=[]
    for s in agg:
        if s not in seen:
            seen.add(s); out.append(s)
    return out
