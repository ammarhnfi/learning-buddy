from fastapi import APIRouter, HTTPException
from app.utils.data_loader import load_all_data
import pandas as pd
from typing import List, Dict, Any

router = APIRouter()

@router.get("/list")
def get_all_roadmaps() -> List[Dict[str, Any]]:
    data = load_all_data()
    lps = data.get("learning_paths", pd.DataFrame())
    
    if lps.empty:
        return []
        
    result = []
    for _, row in lps.iterrows():
        result.append({
            "id": int(row.get("learning_path_id")),
            "name": row.get("learning_path_name")
        })
    return result

@router.get("/{user_email}")
def get_user_roadmap(user_email: str) -> Dict[str, Any]:
    data = load_all_data()
    
    # Load DataFrames
    students = data.get("student_progress", pd.DataFrame())
    courses = data.get("courses", pd.DataFrame())
    lps = data.get("learning_paths", pd.DataFrame())
    
    # Get User Progress
    user_email_clean = user_email.strip().lower()
    user_progress = students[students["email"].astype(str).str.strip().str.lower() == user_email_clean]
    
    completed_courses = set()
    in_progress_courses = set()
    
    for _, row in user_progress.iterrows():
        c_name = row.get("course_name")
        if c_name:
            if str(row.get("is_graduated")) == "1":
                completed_courses.add(c_name)
            else:
                in_progress_courses.add(c_name)
    
    all_lps = []
    
    # Iterate over all Learning Paths
    for _, lp_row in lps.iterrows():
        lp_id = int(lp_row["learning_path_id"])
        lp_name = lp_row["learning_path_name"]
        
        # Get courses for this LP
        lp_courses = courses[courses["learning_path_id"] == lp_id]
        
        course_details = []
        for _, course_row in lp_courses.iterrows():
            c_name = course_row.get("course_name")
            status = "locked" # Default
            
            # Logic for status:
            # If completed -> Lulus
            # If in progress -> Sedang Mempelajari
            # If not started but previous is completed -> Terbuka (implied logic, but for now simplify)
            
            if c_name in completed_courses:
                status = "Lulus"
            elif c_name in in_progress_courses:
                status = "Sedang Mempelajari"
            else:
                # Check if it's the first course or previous is completed
                # For simplicity, just mark as "Belum Diambil"
                status = "Belum Diambil"

            course_details.append({
                "course_id": int(course_row.get("course_id")),
                "course_name": c_name,
                "level": str(course_row.get("course_level_str")),
                "hours": int(course_row.get("hours_to_study")),
                "status": status
            })
            
        all_lps.append({
            "path_id": lp_id,
            "path_name": lp_name,
            "courses": course_details
        })
        
    return {
        "learning_paths": all_lps
    }

@router.get("/{lp_id}")
def get_roadmap_details(lp_id: int) -> Dict[str, Any]:
    # ... (keep existing logic if needed, or remove if unused)
    data = load_all_data()
    lps = data.get("learning_paths", pd.DataFrame())
    courses = data.get("courses", pd.DataFrame())
    
    # Find LP
    lp_row = lps[lps["learning_path_id"] == lp_id]
    if lp_row.empty:
        raise HTTPException(status_code=404, detail="Learning path not found")
        
    lp_name = lp_row.iloc[0]["learning_path_name"]
    
    # Get courses for this LP
    lp_courses = courses[courses["learning_path_id"] == lp_id]
    
    course_list = []
    for _, row in lp_courses.iterrows():
        course_list.append({
            "id": int(row.get("course_id")),
            "name": row.get("course_name"),
            "level": str(row.get("course_level_str")),
            "hours": int(row.get("hours_to_study"))
        })
        
    return {
        "id": lp_id,
        "name": lp_name,
        "courses": course_list
    }
