def skill_match(candidate_skills, job_skills):
    return len(set(candidate_skills) & set(job_skills))
