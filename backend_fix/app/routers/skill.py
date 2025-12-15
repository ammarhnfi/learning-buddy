from fastapi import APIRouter, HTTPException
from typing import Optional
import logging
import pandas as pd
from app.utils.data_loader import load_all_data
from app.services.skill_analyzer import analyze_skill_weakness
from app.services.skill_development_service import get_user_skills_development
from app.services.career_service import match_career

log = logging.getLogger("LearningBuddy.skill")

router = APIRouter()


@router.get("/analyze/{identifier}")
def analyze_skill(identifier: str):
    try:
        data = load_all_data()
        sp: pd.DataFrame = data.get("student_progress", pd.DataFrame())
        if sp.empty:
            raise HTTPException(status_code=404, detail="No student progress data available")

        ident = str(identifier).strip()
        user_email = None
        
        if '@' in ident:
            # treat as email
            user_email_clean = ident.lower()
            user_rows = sp[sp['email'].astype(str).str.strip().str.lower() == user_email_clean]
            user_email = ident
        else:
            # treat as name
            name_clean = ident.lower()
            user_rows = sp[sp['name'].astype(str).str.strip().str.lower() == name_clean]
            # Try to get email from matched rows
            if not user_rows.empty:
                user_email = user_rows.iloc[0].get('email')

        if user_rows.empty:
            raise HTTPException(status_code=404, detail=f"No progress found for {ident}")

        # Aggregate values across rows for the student
        def to_numeric_series(series):
            return pd.to_numeric(series, errors='coerce')

        completed = int(to_numeric_series(user_rows['completed_tutorials']).sum(min_count=1) or 0)
        active = int(to_numeric_series(user_rows['active_tutorials']).sum(min_count=1) or 0)

        # Use mean for scores if multiple rows, ensure no NaN
        submission_rating_val = to_numeric_series(user_rows['submission_rating']).dropna().mean()
        submission_rating = float(submission_rating_val) if not pd.isna(submission_rating_val) else 0.0
        
        exam_score_val = to_numeric_series(user_rows['exam_score']).dropna().mean()
        exam_score = float(exam_score_val) if not pd.isna(exam_score_val) else 0.0

        progress = {
            "completed_tutorials": int(completed),
            "active_tutorials": int(active),
            "submission_rating": float(submission_rating),
            "exam_score": float(exam_score),
        }

        analysis = analyze_skill_weakness(progress)
        
        # Get skill development data (course-based)
        skill_development = {}
        if user_email:
            try:
                skill_development = get_user_skills_development(user_email)
            except Exception as e:
                log.warning("Could not fetch skill development: %s", e)

        return {
            "user": user_email or ident,
            "progress": progress,
            "analysis": analysis,
            "skill_development": skill_development
        }

    except HTTPException:
        raise
    except Exception as e:
        log.exception("Skill analysis failed")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/career/{identifier}")
def get_career_matches(identifier: str):
    """
    Get career profile matches based on user skills.
    """
    try:
        # 1. Reuse logic to get skill development
        # (Ideally refactor to avoid duplication, but for now we call the service directly)
        
        # Resolve email
        data = load_all_data()
        sp = data.get("student_progress", pd.DataFrame())
        ident = identifier.strip()
        user_email = ident # Assume email mostly
        
        if '@' not in ident:
             # try to find email from name
             name_clean = ident.lower()
             user_rows = sp[sp['name'].astype(str).str.strip().str.lower() == name_clean]
             if not user_rows.empty:
                 user_email = user_rows.iloc[0].get('email')
        
        if not user_email:
             raise HTTPException(status_code=404, detail="User not found")

        skill_data = get_user_skills_development(user_email)
        user_skills = skill_data.get("skills", [])
        
        matches = match_career(user_skills)
        
        return {
            "user": user_email,
            "matches": matches
        }
        
    except Exception as e:
        log.exception("Career matching failed")
        raise HTTPException(status_code=500, detail=str(e))
