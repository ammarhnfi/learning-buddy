# app/services/rag_service.py
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple, Dict, List as TypedList
from app.utils.vectorstore import build_or_load_vectorstore
from app.utils.data_loader import build_learningbuddy_kb, load_student_progress, load_all_data
import logging

log = logging.getLogger("LearningBuddy.rag_service")

# Lazy loaded KB
_KB_EMB = None
_KB_DOCS = None

def init_kb(force_rebuild: bool = False):
    global _KB_EMB, _KB_DOCS
    if _KB_EMB is not None and _KB_DOCS is not None and not force_rebuild:
        return _KB_EMB, _KB_DOCS
    texts = build_learningbuddy_kb()
    emb, docs = build_or_load_vectorstore(texts, force_rebuild=force_rebuild)
    _KB_EMB = emb
    _KB_DOCS = docs
    log.info("KB initialized: %d docs, emb shape=%s", len(docs), emb.shape)
    return _KB_EMB, _KB_DOCS

def get_kb():
    if _KB_EMB is None or _KB_DOCS is None:
        return init_kb(False)
    return _KB_EMB, _KB_DOCS

def retrieve_similar(query_vec: np.ndarray, top_k: int = 3) -> List[Tuple[int, float]]:
    """
    query_vec may be 1D or 2D (vector). Returns list of (idx, score) sorted desc.
    """
    emb, docs = get_kb()
    if emb is None or emb.size == 0:
        # Avoid crashing if KB empty
        log.warning("KB embeddings empty or not initialized.")
        return []
        
    q = np.array(query_vec, dtype=float)
    if q.ndim == 2:
        if q.shape[0] != 1:
            q = q[0]
        else:
            q = q.flatten()
            
    if q.ndim != 1:
        # Fallback for safety
        q = q.flatten()
        
    sims = cosine_similarity(q.reshape(1, -1), emb)[0]
    idxs = sims.argsort()[-top_k:][::-1]
    return [(int(i), float(sims[i])) for i in idxs]

def search_progress_by_email(user_email: str):
    """Cari progres belajar berdasarkan email (identifier unik)"""
    records = load_student_progress()
    if not records:
        return None

    user_email = user_email.lower().strip()

    for row in records:
        if str(row.get("email", "")).lower().strip() == user_email:
            return row

    return None

def get_course_info(course_name: str) -> Dict[str, str]:
    """
    Ambil informasi course dari learning_path_answers (via data_loader).
    Mengembalikan dict: summary, description, course_difficulty, technologies, course_type.
    """
    if not course_name:
        return {}

    data = load_all_data()
    lpa = data.get("learning_path_answers")
    if lpa is None or lpa.empty:
        return {}

    course_key = str(course_name).strip().lower()
    lpa = lpa.copy()
    lpa["name_normalized"] = lpa["name"].astype(str).str.strip().str.lower()
    row = lpa[lpa["name_normalized"] == course_key]
    if row.empty:
        return {}

    r = row.iloc[0].fillna("")
    return {
        "summary": str(r.get("summary", "")).strip(),
        "description": str(r.get("description", "")).strip(),
        "course_difficulty": str(r.get("course_difficulty", "")).strip(),
        "technologies": str(r.get("technologies", "")).strip(),
        "course_type": str(r.get("course_type", "")).strip(),
    }

def get_course_tutorials(course_name: str) -> TypedList[str]:
    """
    Ambil daftar tutorial untuk course tertentu dari LP_CourseMapping_clean.csv.
    Return list judul tutorial.
    """
    if not course_name:
        return []

    data = load_all_data()
    mapping = data.get("lp_course_map")
    if mapping is None or mapping.empty:
        return []

    course_key = str(course_name).strip().lower()
    mapping = mapping.copy()
    mapping["course_name_normalized"] = mapping["course_name"].astype(str).str.strip().str.lower()
    rows = mapping[mapping["course_name_normalized"] == course_key]
    if rows.empty:
        return []

    tutorials = rows["tutorial_title"].fillna("").astype(str).tolist()
    return [t for t in tutorials if t.strip()]

def calculate_remaining_requirements(progress: dict, course_tutorials: TypedList[str]) -> Dict[str, float]:
    """
    Hitung kebutuhan yang belum selesai untuk course.
    - total_tutorials: total tutorial di course
    - remaining_tutorials: sisa yang perlu diselesaikan
    - completion_percentage: persen penyelesaian (completed/total)
    """
    try:
        completed = int(progress.get("completed_tutorials") or 0)
    except Exception:
        completed = 0

    total = len(course_tutorials) if course_tutorials else 0
    remaining = max(total - completed, 0)

    completion_pct = 0.0
    if total > 0:
        completion_pct = round(min(max(completed / total * 100, 0), 100), 1)

    return {
        "total_tutorials": total,
        "remaining_tutorials": remaining,
        "completion_percentage": completion_pct,
    }
