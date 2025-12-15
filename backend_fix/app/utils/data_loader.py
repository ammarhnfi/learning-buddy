# app/utils/data_loader.py
from pathlib import Path
import pandas as pd
from typing import List, Dict
import logging
import os

log = logging.getLogger("LearningBuddy.data_loader")
DATA_DIR = Path("data")

CSV_FILES = {
    "course_levels": "CourseLevel_clean.csv",
    "courses": "Courses_clean.csv",
    "current_interest": "CurrentInterestQuestions_clean.csv",
    "current_tech": "CurrentTechQuestions_clean.csv",
    "learning_path_answers": "LearningPathAnswer_clean.csv",
    "learning_paths": "LearningPath_clean.csv",
    "lp_course_map": "LP_CourseMapping_clean.csv",
    "skill_keywords": "SkillKeywords_clean.csv",
    "student_progress": "StudentProgress_clean.csv",
    "tutorials": "Tutorials_clean.csv",
}

def _read_csv(key: str) -> pd.DataFrame:
    p = DATA_DIR / CSV_FILES[key]
    if not p.exists():
        log.warning("Missing CSV file: %s", p)
        return pd.DataFrame()
    try:
        # try to infer encoding if possible, fallback to utf-8
        return pd.read_csv(p)
    except Exception as e:
        log.error("Failed to read %s: %s", p, e)
        try:
            return pd.read_csv(p, encoding="latin-1")
        except Exception as e2:
            log.error("Second attempt failed reading %s: %s", p, e2)
            return pd.DataFrame()

def load_all_data() -> Dict[str, pd.DataFrame]:
    """Return a dict of dataframes for each known CSV."""
    return {k: _read_csv(k) for k in CSV_FILES.keys()}

def get_enriched_courses() -> pd.DataFrame:
    """
    Merge Courses dengan LearningPathAnswer dan CourseLevel untuk mendapatkan
    informasi course yang lebih lengkap.
    Returns enriched courses dataframe.
    """
    data = load_all_data()
    courses = data.get("courses", pd.DataFrame())
    lpa = data.get("learning_path_answers", pd.DataFrame())
    course_levels = data.get("course_levels", pd.DataFrame())
    
    if courses.empty:
        log.warning("Courses dataframe is empty")
        return pd.DataFrame()
    
    # Start with courses
    enriched = courses.copy()
    
    # Merge with LearningPathAnswer (by course_name)
    if not lpa.empty:
        # Normalize course names for matching
        enriched_temp = enriched.copy()
        enriched_temp['course_name_normalized'] = enriched_temp['course_name'].astype(str).str.strip().str.lower()
        
        lpa_temp = lpa.copy()
        lpa_temp['name_normalized'] = lpa_temp['name'].astype(str).str.strip().str.lower()
        
        # Merge
        enriched = enriched_temp.merge(
            lpa_temp[['name_normalized', 'summary', 'description', 'course_difficulty', 'technologies', 
                     'course_type', 'courseMeta', 'courseInfo']],
            left_on='course_name_normalized',
            right_on='name_normalized',
            how='left',
            suffixes=('', '_lpa')
        )
        
        # Drop temporary columns
        enriched = enriched.drop(columns=['course_name_normalized', 'name_normalized'], errors='ignore')
    
    # Merge with CourseLevel (by course_level_str)
    if not course_levels.empty:
        # Convert course_level_str to numeric for matching
        enriched['course_level_num'] = pd.to_numeric(enriched['course_level_str'], errors='coerce')
        
        enriched = enriched.merge(
            course_levels[['id', 'course_level']],
            left_on='course_level_num',
            right_on='id',
            how='left',
            suffixes=('', '_level')
        )
        
        # Rename for clarity
        if 'course_level' in enriched.columns:
            enriched = enriched.rename(columns={'course_level': 'course_level_name'})
        
        # Drop temporary columns
        enriched = enriched.drop(columns=['course_level_num', 'id'], errors='ignore')
    
    log.info(f"Enriched courses: {len(enriched)} courses with merged data")
    return enriched

# -----------------------------
# BUILD KB: per-user documents +
# global docs for courses/tutorials etc.
# -----------------------------
def build_learningbuddy_kb() -> List[str]:
    """
    Build KB texts from CSVs:
      - global course/tut/tutorial descriptions
      - question banks
      - per-user student progress docs (rich)
    Returns list[str] (documents).
    """
    data = load_all_data()
    docs: List[str] = []

    # GLOBAL: courses (use enriched version with merged data)
    # Note: LearningPathAnswer data is now merged into courses, so we don't need separate COURSE_META
    courses = get_enriched_courses()
    if not courses.empty:
        for _, r in courses.fillna("").astype(str).iterrows():
            # Build course document with enriched information
            course_parts = [
                r.get("course_name", ""),
                r.get("course_level_str", ""),
                r.get("course_level_name", ""),  # From CourseLevel merge
                str(r.get("hours_to_study", "")),
                r.get("summary", ""),  # From LearningPathAnswer merge
                r.get("course_difficulty", ""),  # From LearningPathAnswer merge
                r.get("technologies", ""),  # From LearningPathAnswer merge
            ]
            # Filter empty parts
            course_text = " | ".join([p for p in course_parts if p.strip()])
            if course_text:
                docs.append(f"COURSE: {course_text}")
            
            # Also add description separately if available (can be long)
            description = r.get("description", "").strip()
            if description:
                # Truncate very long descriptions to avoid huge documents
                if len(description) > 1000:
                    description = description[:1000] + "..."
                docs.append(f"COURSE_DESC: {r.get('course_name', '')} | {description}")

    # GLOBAL: tutorials mapping
    mapping = data.get("lp_course_map", pd.DataFrame())
    if not mapping.empty:
        for _, r in mapping.fillna("").astype(str).iterrows():
            docs.append("MAPPING: " + " | ".join([r.get("learning_path_name",""), r.get("course_name",""), r.get("tutorial_title","")]))

    # GLOBAL: tutorials
    tutorials = data.get("tutorials", pd.DataFrame())
    if not tutorials.empty:
        for _, r in tutorials.fillna("").astype(str).iterrows():
            t = r.get("tutorial_title","")
            if t.strip():
                docs.append("TUTORIAL: " + t)

    # QUESTIONS datasets (useful for quiz/eval)
    ci = data.get("current_interest", pd.DataFrame())
    if not ci.empty:
        for _, r in ci.fillna("").astype(str).iterrows():
            docs.append("Q_INTEREST: " + " | ".join([r.get("question_desc",""), r.get("option_text","")]))

    ct = data.get("current_tech", pd.DataFrame())
    if not ct.empty:
        for _, r in ct.fillna("").astype(str).iterrows():
            docs.append("Q_TECH: " + " | ".join([r.get("question_desc",""), r.get("tech_category","")]))

    # PER-USER: student progress -> create a rich user doc for each student
    sp = data.get("student_progress", pd.DataFrame())
    if not sp.empty:
        # normalize columns we expect (coerce missing)
        sp = sp.fillna("")
        for _, r in sp.astype(str).iterrows():
            name = r.get("name","").strip()
            if not name:
                continue
            course = r.get("course_name","")
            completed = r.get("completed_tutorials","")
            active = r.get("active_tutorials","")
            graduated = r.get("is_graduated","")
            exam_score = r.get("exam_score","")
            # create per-user doc with fields that can be used by RAG
            doc = [
                f"USER: {name}",
                f"CURRENT_COURSE: {course}",
                f"COMPLETED_TUTORIALS: {completed}",
                f"ACTIVE_TUTORIALS: {active}",
                f"IS_GRADUATED: {graduated}",
                f"EXAM_SCORE: {exam_score}",
                "SKILLS_STRONG: To be computed",
                "SKILLS_WEAK: To be computed",
                "INSIGHTS: To be computed by ML"
            ]
            docs.append(" | ".join([d for d in doc if d]))
    # final cleanup and return
    docs = [d.strip() for d in docs if d and d.strip()]
    return docs

# -----------------------------
# Backwards-compatible alias:
# older generate_vectors.py called load_all_data_texts()
# keep alias so older scripts continue to work
# -----------------------------
def load_all_data_texts() -> List[str]:
    """
    Compatibility wrapper for older code that expects load_all_data_texts().
    Returns the same as build_learningbuddy_kb().
    """
    return build_learningbuddy_kb()

def load_student_progress(path: str = None):
    """Return list of dict records from student progress CSV."""
    if path is None:
        path = str(DATA_DIR / "StudentProgress_clean.csv")
    if not os.path.exists(path):
        return []
    try:
        df = pd.read_csv(path)
    except Exception:
        df = pd.read_csv(path, encoding="latin-1")
    records = df.to_dict(orient="records")
    return records