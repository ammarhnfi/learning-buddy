import pandas as pd
from app.utils.data_loader import load_all_data
import logging

log = logging.getLogger("LearningBuddy.smart_recommender")


def get_smart_recommendation(user_identifier: str, top_n: int = 5, interests_override: list | None = None):
    """Return smart course recommendations for a user.

    The function accepts either a user name or an email address. If the
    provided identifier looks like an email (contains '@'), it will match
    against the `email` column in StudentProgress. Otherwise it matches by
    `name` (case-insensitive).
    """
    data = load_all_data()
    students = data.get("student_progress", pd.DataFrame())
    courses = data.get("courses", pd.DataFrame())

    if students.empty or "name" not in students.columns:
        raise ValueError("StudentProgress CSV missing or malformed.")

    if courses.empty or "course_level_str" not in courses.columns:
        raise ValueError("Courses CSV missing required fields.")

    # Normalize and create helper columns
    identifier = str(user_identifier or "").strip()
    is_email = "@" in identifier and "." in identifier.split("@")[-1]

    students["name_clean"] = students["name"].astype(str).str.strip().str.lower()
    students["email_clean"] = students.get("email", "").astype(str).str.strip().str.lower()

    if is_email:
        key = identifier.lower()
        user_row = students[students["email_clean"] == key]
        log.debug("Matching recommender by email: %s -> %d rows", key, len(user_row))
    else:
        key = identifier.lower()
        user_row = students[students["name_clean"] == key]
        log.debug("Matching recommender by name: %s -> %d rows", key, len(user_row))

    # Ensure courses have numeric level for sorting
    courses = courses.copy()
    courses["course_level_str"] = pd.to_numeric(courses["course_level_str"], errors="coerce")

    # No history -> beginner roadmap
    if user_row.empty:
        beginner = courses.sort_values("course_level_str").head(top_n)
        return beginner[["course_name", "course_level_str", "hours_to_study"]].to_dict(orient="records")

    # Use latest record for the user
    latest = user_row.iloc[-1]
    last_taken = str(latest.get("course_name", "")).strip()

    # Try to find last course in catalog (compare stripped strings)
    last_course_row = courses[courses["course_name"].astype(str).str.strip() == last_taken]

    if last_course_row.empty:
        # If unmatched, fallback to entry courses
        return courses.sort_values("course_level_str").head(top_n)[["course_name", "course_level_str", "hours_to_study"]].to_dict(orient="records")

    last_level = int(last_course_row.iloc[0]["course_level_str"])

    # Recommend 1–2 levels ahead
    candidates = courses[
        (courses["course_level_str"] > last_level) &
        (courses["course_level_str"] <= last_level + 2)
    ].sort_values("course_level_str")
    # If an interests override is provided, use it. Otherwise derive interests
    data = load_all_data()
    skill_kw_df = data.get("skill_keywords", pd.DataFrame())
    keywords = []
    if not skill_kw_df.empty and "keyword" in skill_kw_df.columns:
        keywords = [str(k).strip().lower() for k in skill_kw_df["keyword"].fillna("") if str(k).strip()]

    # Derive interests from student's course history (all rows for that student)
    derived_interests = set()
    if interests_override:
        derived_interests = set([i.strip().lower() for i in interests_override if i and i.strip()])
    else:
        history_courses = [str(c).strip().lower() for c in user_row.get("course_name", []) if str(c).strip()]
        for kw in keywords:
            for cname in history_courses:
                if kw in cname:
                    derived_interests.add(kw)
                    break

    # If no derived interests, fall back to returning candidates as before
    if not derived_interests:
        return candidates.head(top_n)[["course_name", "course_level_str", "hours_to_study"]].to_dict(orient="records")

    # Score candidates by how many interest keywords they match
    def score_candidate(row):
        name = str(row.get("course_name", "")).lower()
        matches = [kw for kw in derived_interests if kw in name]
        return len(matches), matches

    scored = []
    for _, r in candidates.iterrows():
        count, matches = score_candidate(r)
        scored.append((count, matches, r))

    # Sort by match count desc, then by level asc
    scored_sorted = sorted(scored, key=lambda t: (-t[0], t[2].get("course_level_str", 0)))

    results = []
    for count, matches, row in scored_sorted:
        reason = None
        score = 0.0
        if count > 0:
            reason = f"Matches interest: {', '.join(matches)}"
            # simple score: proportion of matched keywords (capped to 1.0)
            score = min(1.0, count / max(1, len(derived_interests)))
        results.append({
            "course_name": row.get("course_name"),
            "course_level_str": row.get("course_level_str"),
            "hours_to_study": row.get("hours_to_study"),
            "score": score,
            "reason": reason,
        })

    # Return top_n, prioritizing matched items; if not enough matched, next items will have score 0
    return results[:top_n]
