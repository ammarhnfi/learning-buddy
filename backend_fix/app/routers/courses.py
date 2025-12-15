import pandas as pd
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import os
import ast

router = APIRouter()

# Global cache for data (CSV Fallback)
COURSES_DATA = None
LP_ANSWERS_DATA = None
TUTORIALS_DATA = None

def load_data():
    global COURSES_DATA, LP_ANSWERS_DATA, TUTORIALS_DATA
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir = os.path.join(base_path, "data")
    
    if COURSES_DATA is None:
        COURSES_DATA = pd.read_csv(os.path.join(data_dir, "Courses_clean.csv"))
    
    if LP_ANSWERS_DATA is None:
        LP_ANSWERS_DATA = pd.read_csv(os.path.join(data_dir, "LearningPathAnswer_clean.csv"))
        
    if TUTORIALS_DATA is None:
        TUTORIALS_DATA = pd.read_csv(os.path.join(data_dir, "Tutorials_clean.csv"))

@router.get("/{course_id}")
def get_course_detail(course_id: int):
    print(f"Fetching details for course_id: {course_id}")
    load_data()
    
    # 1. Find Course in Courses_clean.csv (Base Info)
    course_row = COURSES_DATA[COURSES_DATA['course_id'] == int(course_id)]
    
    if course_row.empty:
        print(f"Course ID {course_id} not found in Courses_clean.csv")
        raise HTTPException(status_code=404, detail="Course not found")
    
    course_base = course_row.iloc[0].to_dict()
    course_name = course_base['course_name']
    
    # 2. Find Rich Info in LearningPathAnswer_clean.csv
    # Try matching by ID first (assuming 'id' column matches course_id)
    rich_info = {}
    
    # Check if 'id' column exists and try to match
    if 'id' in LP_ANSWERS_DATA.columns:
        lp_row = LP_ANSWERS_DATA[LP_ANSWERS_DATA['id'] == int(course_id)]
    else:
        lp_row = pd.DataFrame()

    # Fallback: Match by Name if ID match fails
    if lp_row.empty:
        lp_row = LP_ANSWERS_DATA[LP_ANSWERS_DATA['name'] == course_name]
        
    if not lp_row.empty:
        rich_data = lp_row.iloc[0].to_dict()
        
        # Parse courseMeta ['140 Jam', '4,84', 'Menengah']
        meta = []
        try:
            if isinstance(rich_data.get('courseMeta'), str):
                meta = ast.literal_eval(rich_data['courseMeta'])
        except:
            meta = []
            
        # Parse courseInfo ['107 Modul', '41.831 Siswa Terdaftar']
        info = []
        try:
            if isinstance(rich_data.get('courseInfo'), str):
                info = ast.literal_eval(rich_data['courseInfo'])
        except:
            info = []

        rich_info = {
            "summary": rich_data.get('summary', ''),
            "description": rich_data.get('description', ''),
            "difficulty": rich_data.get('course_difficulty', ''),
            "price": rich_data.get('course_price', ''),
            "technologies": rich_data.get('technologies', '').split(',') if isinstance(rich_data.get('technologies'), str) else [],
            "type": rich_data.get('course_type', ''),
            "rating": meta[1] if len(meta) > 1 else None,
            "total_modules": info[0] if len(info) > 0 else None,
            "total_students": info[1] if len(info) > 1 else None
        }
    else:
        # Defaults if not found in rich CSV
        rich_info = {
            "summary": "",
            "description": "Deskripsi belum tersedia.",
            "difficulty": course_base.get('course_level_str', 'N/A'),
            "price": "N/A",
            "technologies": [],
            "type": "Reguler",
            "rating": None,
            "total_modules": None,
            "total_students": None
        }

    # 3. Get Tutorials
    tutorials = TUTORIALS_DATA[TUTORIALS_DATA['course_id'] == int(course_id)]
    tutorial_list = tutorials[['tutorial_title']].to_dict('records')
    
    return {
        "course_id": course_id,
        "course_name": course_name,
        "level": rich_info['difficulty'] or course_base.get('course_level_str', 'N/A'),
        "hours": int(course_base.get('hours_to_study', 0)),
        "description": rich_info['description'],
        "summary": rich_info['summary'],
        "price": rich_info['price'],
        "technologies": rich_info['technologies'],
        "type": rich_info['type'],
        "rating": rich_info['rating'],
        "total_modules": rich_info['total_modules'],
        "total_students": rich_info['total_students'],
        "tutorials": [t['tutorial_title'] for t in tutorial_list]
    }
