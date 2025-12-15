from fastapi import APIRouter, HTTPException
from app.utils.data_loader import load_all_data
import pandas as pd
import math

router = APIRouter()

@router.get("/users")
async def get_all_users():
    data = load_all_data()
    sp = data.get("student_progress", pd.DataFrame())
    
    if sp.empty:
        return []
        
    # Get unique users by email and sort by name
    users = sp[['name', 'email']].drop_duplicates(subset=['email']).sort_values(by='name').to_dict('records')
    return users

@router.get("/{user_email}")
async def get_dashboard_data(user_email: str):
    data = load_all_data()
    
    # 1. Get User Info & Progress
    sp = data.get("student_progress", pd.DataFrame())
    courses_df = data.get("courses", pd.DataFrame())
    
    # Normalize email for comparison
    user_email_clean = user_email.strip().lower()
    user_progress = sp[sp['email'].astype(str).str.strip().str.lower() == user_email_clean]
    
    if user_progress.empty:
        # Return default structure for new/unknown user
        return {
            "user": {"name": "User", "email": user_email},
            "stats": {"completed": 0, "in_progress": 0, "average_score": 0, "total_hours": 0},
            "courses": []
        }

    user_name = user_progress.iloc[0]['name']
    
    # 2. Build Enrolled Course List with Details
    course_list = []
    total_hours_spent = 0
    total_score = 0
    score_count = 0
    completed_count = 0
    
    # Create a lookup for course details by name
    # Note: StudentProgress has course_name, Courses has course_name. 
    # Ideally we match by ID, but SP doesn't have course_id.
    # Build lookup by normalized course name (case-insensitive)
    course_info_map = {}
    for _, row in courses_df.iterrows():
        name_key = str(row.get('course_name', '')).strip().lower()
        try:
            total_hours_val = int(row.get('hours_to_study')) if pd.notna(row.get('hours_to_study')) else 0
        except Exception:
            try:
                total_hours_val = int(float(row.get('hours_to_study', 0)))
            except Exception:
                total_hours_val = 0

        course_info_map[name_key] = {
            "id": row.get('course_id'),
            "level": str(row.get('course_level_str')),
            "total_hours": total_hours_val
        }
        
    level_map = {
        "1": "Dasar",
        "2": "Pemula",
        "3": "Menengah",
        "4": "Mahir",
        "5": "Profesional"
    }

    for _, row in user_progress.iterrows():
        c_name_raw = row.get('course_name', '')
        c_name = str(c_name_raw)
        c_key = c_name.strip().lower()

        # Try exact normalized match; if not found, provide fallback entry so UI still shows course
        if c_key in course_info_map:
            c_info = course_info_map[c_key]
        else:
            # Fallback: unknown id/level, zero hours — still include the course to avoid hiding user's progress
            c_info = {"id": None, "level": "0", "total_hours": 0}
        
        # Calculate Progress
        # Normalize numeric progress fields
        try:
            active_tutorials = float(row.get('active_tutorials')) if pd.notna(row.get('active_tutorials')) else 1
        except Exception:
            active_tutorials = 1
        try:
            completed_tutorials = float(row.get('completed_tutorials')) if pd.notna(row.get('completed_tutorials')) else 0
        except Exception:
            completed_tutorials = 0
        
        # Cap completion at active
        if completed_tutorials > active_tutorials:
            completed_tutorials = active_tutorials
            
        progress_pct = (completed_tutorials / active_tutorials) if active_tutorials > 0 else 0
        
        # Calculate Hours Spent
        total_hours = c_info.get('total_hours', 0) or 0
        hours_spent = int(progress_pct * total_hours)
        total_hours_spent += hours_spent
        
        # Get Score
        score = 0
        if pd.notna(row.get('exam_score')):
             score = float(row['exam_score'])
        elif pd.notna(row.get('submission_rating')):
             # Convert 1-5 rating to 0-100 scale roughly
             score = float(row['submission_rating']) * 20
        
        if score > 0:
            total_score += score
            score_count += 1
            
        # Status
        is_graduated = str(row['is_graduated']) == "1"
        status = "Lulus" if is_graduated else "Sedang Mempelajari"
        if is_graduated:
            completed_count += 1
            progress_pct = 1.0 # Ensure 100% if graduated
            hours_spent = total_hours

        course_list.append({
            "id": c_info['id'],
            "title": c_name,
            "level": level_map.get(c_info['level'], "Unknown"),
            "total_hours": total_hours,
            "hours_spent": hours_spent,
            "progress_pct": int(progress_pct * 100),
            "score": int(score) if score > 0 else None,
            "status": status
        })

    # 3. Calculate Aggregate Stats
    avg_score = int(total_score / score_count) if score_count > 0 else 0
    
    return {
        "user": {
            "name": user_name,
            "email": user_email,
            "avatar": "https://ui-avatars.com/api/?name=" + user_name.replace(" ", "+")
        },
        "stats": {
            "completed": completed_count,
            "in_progress": len(course_list) - completed_count,
            "average_score": avg_score,
            "total_hours": total_hours_spent
        },
        "courses": course_list
    }
