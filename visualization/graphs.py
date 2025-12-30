def generate_skill_dag(target_role, matched_skills, missing_skills):
    """
    Creates a Mermaid.js string representing the professional gap.
    Shows the target role branching into matched (green) and missing (red) skills.
    """
    # Sanitize IDs to be safe for Mermaid (no spaces or special chars)
    def clean_id(s):
        return s.replace(" ", "_").replace("-", "_").replace(".", "_")

    role_id = clean_id(target_role)
    
    graph = "graph TD\n"
    # Root Node
    graph += f"  {role_id}(({target_role}))\n"
    
    # Matched Skills
    for s in matched_skills:
        s_id = clean_id(s)
        graph += f"  {role_id} --- {s_id}[{s}]:::matched\n"
    
    # Missing Skills
    for s in missing_skills:
        s_id = clean_id(s)
        graph += f"  {role_id} --- {s_id}[{s}]:::missing\n"
        
    # Styling classes
    graph += "\n  classDef matched fill:#d1fae5,stroke:#10b981\n"
    graph += "  classDef missing fill:#fee2e2,stroke:#ef4444\n"
    
    return graph

def skill_graph(role, skills):
    """
    Legacy wrapper for compatibility if needed, 
    but app.py should switch to generate_skill_dag
    """
    return generate_skill_dag(role, skills, [])
