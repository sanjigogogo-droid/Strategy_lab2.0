def compare_resume(old, new):
    changes = {}

    old_skills = set(old.get("skills", []))
    new_skills = set(new.get("skills", []))

    added = new_skills - old_skills
    if added:
        changes["skills_added"] = list(added)

    if new["experience_years"] > old["experience_years"]:
        changes["experience_change"] = (
            old["experience_years"],
            new["experience_years"]
        )

    changes["semantic_similarity"] = round(new.get("semantic_score", 0.85), 2)
    return changes
