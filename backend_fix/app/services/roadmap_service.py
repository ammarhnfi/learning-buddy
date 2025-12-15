# app/services/roadmap_service.py

import pandas as pd
from rapidfuzz import process, fuzz
from app.utils.data_loader import load_all_data
import logging

log = logging.getLogger("LearningBuddy.roadmap")

def fuzzy_match_course(user_course: str, course_list: list):
    """
    Fuzzy matching antara nama mata kuliah user dan course resmi.
    Mengembalikan nama course resmi agar konsisten.
    """
    if not isinstance(user_course, str) or not user_course.strip():
        return None

    user_clean = user_course.strip().lower()

    # Hindari match ke string kosong atau invalid
    if user_clean in ["nan", "none", "-", ""]:
        return None

    choices = [c.lower().strip() for c in course_list]

    result = process.extractOne(
        user_clean,
        choices,
        scorer=fuzz.token_sort_ratio
    )

    if not result:
        return None

    match, score, idx = result

    # Ambang batas skor similarity agar tidak asal match
    if score < 70:  
        return None

    return course_list[idx]


def recommend_courses_for_user(user_email: str, top_n: int = 3):
    data = load_all_data()
    students = data.get("student_progress", pd.DataFrame())
    courses = data.get("courses", pd.DataFrame())

    # Validasi minimal
    if students.empty or "email" not in students.columns:
        log.warning("StudentProgress CSV missing or has no 'email' column.")
        if courses.empty:
            return []
        return courses.head(top_n)[["course_name", "course_level_str", "hours_to_study"]].to_dict(orient="records")

    if "course_level_str" not in courses.columns:
        log.warning("courses CSV missing column: course_level_str")
        return []

    if "course_name" not in courses.columns:
        log.warning("courses CSV missing column: course_name")
        return []

    # Normalisasi email
    user_email_clean = user_email.strip().lower()
    students["email_clean"] = students["email"].astype(str).str.strip().str.lower()

    courses["course_name_clean"] = (
        courses["course_name"].astype(str).str.strip().str.lower()
    )

    courses["course_level_str"] = pd.to_numeric(
        courses["course_level_str"], errors="coerce"
    )

    # HAPUS DUPLIKASI COURSE
    courses = courses.drop_duplicates(subset=["course_name"], keep="first")

    # Hapus course tanpa level (NaN)
    courses = courses.dropna(subset=["course_level_str"])

    # Sort by course level
    courses = courses.sort_values("course_level_str").reset_index(drop=True)

    # Ambil user row by email
    user_row = students[students["email_clean"] == user_email_clean]

    if user_row.empty:
        # Jika user baru/tidak ada progress, sarankan level terendah (biasanya Level 1)
        return courses.head(top_n)[
            ["course_name", "course_level_str", "hours_to_study"]
        ].to_dict(orient="records")

    # Ambil last known course dari user
    raw_course_name = str(user_row.iloc[0].get("course_name", "")).strip()

    # Jika progress kosong
    if raw_course_name.lower() in ["", "nan", "-", "none"]:
        return courses.head(top_n)[
            ["course_name", "course_level_str", "hours_to_study"]
        ].to_dict(orient="records")

    # Fuzzy match untuk mencocokkan course name user dengan database courses
    official_names = courses["course_name"].astype(str).tolist()
    matched_course = fuzzy_match_course(raw_course_name, official_names)

    if matched_course is None:
        # Fallback jika tidak match: just recommend top beginner courses
        return courses.head(top_n)[
            ["course_name", "course_level_str", "hours_to_study"]
        ].to_dict(orient="records")

    user_course_row = courses[courses["course_name"] == matched_course]

    if user_course_row.empty:
        user_level = 1
    else:
        user_level = int(user_course_row.iloc[0]["course_level_str"])

    # Filter level lebih tinggi (Progressive recommendation)
    # Rekomendasikan course dengan level > user_level
    candidates = courses[courses["course_level_str"] > user_level]

    if candidates.empty:
        # Jika sudah level max, rekomendasikan course lain di level yang sama atau semua sisa course
        candidates = courses[courses["course_name"] != matched_course]

    final = candidates.head(top_n)

    cols = ["course_name", "course_level_str", "hours_to_study"]
    final = final[cols]

    return final.to_dict(orient="records")