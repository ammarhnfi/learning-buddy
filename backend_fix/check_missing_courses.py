import pandas as pd
import sys
import os

# Add app to path
sys.path.append(os.getcwd())

from app.services.skill_development_service import COURSE_SKILL_MAP
from app.utils.data_loader import load_all_data

def check_missing():
    try:
        data = load_all_data()
        sp = data.get("student_progress", pd.DataFrame())
        
        if sp.empty:
            print("No student progress data found.")
            return

        all_courses = sp['course_name'].unique()
        
        missing = []
        for course in all_courses:
            c_name = str(course).strip()
            if c_name not in COURSE_SKILL_MAP:
                missing.append(c_name)
                
        print(f"Total Unique Courses: {len(all_courses)}")
        print(f"Mapped Courses: {len(COURSE_SKILL_MAP)}")
        print(f"Missing Courses: {len(missing)}")
        print("\n--- Missing Course Names ---")
        for m in sorted(missing):
            print(f'"{m}": [],')
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_missing()
