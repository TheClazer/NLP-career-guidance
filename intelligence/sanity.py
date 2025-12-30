def sanity_check_role_baseline(rb: dict):
    if not rb.get("role") or len(rb.get("required_skills", [])) < 1:
        return False, "role must exist and have at least one required skill"
    for w in rb.get("weights", {}).values():
        val = w
        try:
           val = int(val)
        except:
           return False, "weights must be integers"
           
        if not (1 <= val <= 5):
            return False, "weights must be in 1..5"
    return True, None
