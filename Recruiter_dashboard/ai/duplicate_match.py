def is_probable_duplicate(a, b):
    score = 0
    if a["email"] == b["email"]:
        score += 0.6
    if a["phone"] == b["phone"]:
        score += 0.3
    if a["full_name"] == b["full_name"]:
        score += 0.1
    return score >= 0.7
