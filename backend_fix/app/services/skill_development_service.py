# app/services/skill_development_service.py
import pandas as pd
from typing import Dict, List
from app.utils.data_loader import load_all_data
import logging

log = logging.getLogger("LearningBuddy.skill_development")

# Manually mapped: course names to primary skills they teach
COURSE_SKILL_MAP = {
    # AI & Machine Learning courses
    "Belajar Dasar AI": ["Python", "Machine Learning", "Data Analysis"],
    "Belajar Fundamental Deep Learning": ["Python", "TensorFlow", "Deep Learning", "Machine Learning"],
    "Belajar Machine Learning untuk Pemula": ["Python", "Machine Learning", "Data Analysis", "SQL"],
    "Machine Learning Terapan": ["Python", "Machine Learning", "Data Science"],
    "Membangun Proyek Deep Learning Tingkat Mahir": ["Python", "TensorFlow", "Deep Learning", "Cloud Computing"],
    
    # Python & General Programming
    "Memulai Pemrograman dengan Python": ["Python", "Pemrograman", "System Administration"],
    
    # Android Development
    "Belajar Fundamental Aplikasi Android": ["Android", "Java", "Kotlin", "Mobile Development"],
    "Belajar Membuat Aplikasi Android untuk Pemula": ["Android", "Java", "Mobile Development"],
    "Belajar Pengembangan Aplikasi Android Intermediate": ["Android", "Kotlin", "Mobile Development", "Material Design"],
    "Belajar Membangun Aplikasi Android Native Bagian I": ["Android", "Java", "Mobile Development"],
    "Memulai Pemrograman dengan Kotlin": ["Kotlin", "Android", "Pemrograman"],
    "Menjadi Android Developer Expert": ["Android", "Kotlin", "Java", "Mobile Development", "Performance Optimization"],
    
    # SOLID Principles & Architecture
    "Belajar Prinsip Pemrograman SOLID": ["SOLID", "OOP", "Code Architecture", "Design Patterns"],
    
    # AWS & Cloud
    "Architecting on AWS (Membangun Arsitektur Cloud di AWS)": ["Amazon Web Services", "Cloud Computing", "AWS Architecture"],
    "Belajar Dasar Cloud dan Gen AI di AWS": ["Amazon Web Services", "Cloud Computing", "AI"],
    
    # JavaScript & Backend
    "Belajar Dasar Pemrograman JavaScript": ["JavaScript", "Web", "Frontend"],
    "Belajar Back-End Pemula dengan JavaScript": ["JavaScript", "Node.js", "Backend", "API Development"],
    "Belajar Fundamental Back-End dengan JavaScript": ["JavaScript", "Node.js", "Express.js", "Backend", "Database"],
    "Menjadi Back-End Developer Expert dengan JavaScript": ["JavaScript", "Node.js", "Backend", "API", "Cloud Computing"],
    "Menjadi Node.js Application Developer": ["Node.js", "JavaScript", "Backend", "API Development"],
    
    # Python Backend
    "Belajar Back-End Pemula dengan Python": ["Python", "Backend", "Web", "Database"],
    "Belajar Fundamental Back-End dengan Python": ["Python", "Django/Flask", "Backend", "Database", "API"],
    
    # Google Cloud
    "Belajar Dasar Google Cloud": ["Google Cloud", "Cloud Computing"],
    "Menjadi Google Cloud Architect": ["Google Cloud", "Cloud Architecture", "System Design"],
    "Menjadi Google Cloud Engineer": ["Google Cloud", "Cloud Computing", "Infrastructure"],
    
    # Data Science & Analytics
    "Belajar Analisis Data dengan Python": ["Python", "Data Analysis", "Pandas", "Excel"],
    "Belajar Dasar Data Science": ["Data Science", "Python", "Statistics"],
    "Belajar Dasar Structured Query Language (SQL)": ["SQL", "Database", "MySQL"],
    "Belajar Matematika untuk Data Science": ["Mathematics", "Statistics", "Data Science"],
    "Belajar Penerapan Data Science": ["Data Science", "Machine Learning", "Python"],
    
    # DevOps
    "Belajar Dasar-Dasar DevOps": ["DevOps", "Linux", "Automation"],
    "Belajar Implementasi CI/CD": ["CI/CD", "DevOps", "Automation", "Jenkins"],
    "Belajar Jaringan Komputer untuk Pemula": ["Networking", "TCP/IP", "Linux"],
    "Belajar Membangun Arsitektur Microservices": ["Microservices", "Architecture", "Cloud"],
    "Menjadi Linux System Administrator": ["Linux", "System Administration", "Networking"],
    
    # Web Development & Frontend
    "Belajar Dasar Pemrograman Web": ["Web", "HTML", "CSS", "JavaScript"],
    "Belajar Fundamental Front-End Web Development": ["Frontend", "JavaScript", "ReactJS", "CSS"],
    "Belajar Membuat Front-End Web untuk Pemula": ["Frontend", "HTML", "CSS", "JavaScript"],
    "Belajar Pengembangan Web Intermediate": ["Frontend", "JavaScript", "Web", "Bootstrap"],
    
    # AI & Prompt Engineering
    "Prompt Engineering untuk Software Developer": ["AI", "Generative AI", "Prompt Engineering"],
    
    # iOS Development
    "Belajar Fundamental Aplikasi iOS": ["Swift", "iOS", "Mobile Development"],
    "Belajar Membuat Aplikasi iOS untuk Pemula": ["Swift", "iOS", "Mobile Development"],
    "Memulai Pemrograman Dengan Swift": ["Swift", "iOS", "Pemrograman"],
    "Menjadi iOS Developer Expert": ["Swift", "iOS", "Mobile Development", "Performance"],
    
    # Flutter Development
    "Belajar Fundamental Aplikasi Flutter": ["Flutter", "Dart", "Mobile Development"],
    "Belajar Membuat Aplikasi Flutter untuk Pemula": ["Flutter", "Dart", "Mobile Development"],
    "Belajar Pengembangan Aplikasi Flutter Intermediate": ["Flutter", "Dart", "Mobile Development", "UI"],
    "Memulai Pemrograman dengan Dart": ["Dart", "Flutter", "Pemrograman"],
    "Menjadi Flutter Developer Expert": ["Flutter", "Dart", "Mobile Development", "Performance"],
    
    # React
    "Belajar Fundamental Aplikasi Web dengan React": ["ReactJS", "JavaScript", "Frontend"],
    "Belajar Membuat Aplikasi Web dengan React": ["ReactJS", "JavaScript", "Frontend", "Web"],
    "Menjadi React Web Developer Expert": ["ReactJS", "JavaScript", "Frontend", "Web", "Performance"],
    
    # MLOps
    "Machine Learning Operations (MLOps)": ["MLOps", "Machine Learning", "DevOps", "Python"],
    "Membangun Sistem Machine Learning": ["Machine Learning", "System Design", "Python"],
    
    # LINE Chatbot
    "Belajar Membangun LINE Chatbot": ["Chatbot", "API", "Bot Development"],

    # Newly Mapped Courses
    "AI Praktis untuk Produktivitas": ["AI", "Productivity"],
    "Asah 2025 - Kuis ILT FEBE AI": ["AI", "Frontend", "Backend"],
    "Asah 2025 - Kuis ILT Soft Skill": ["Soft Skills"],
    "BDT 2022 (Tahap 2) Pre-Test Analisis Data": ["Data Analysis"],
    "BDT 2022 (Tahap 2) Pre-Test Android Developer Dasar": ["Android"],
    "BDT 2022 (Tahap 2) Pre-Test IT Support": ["IT Support"],
    "BDT 2022 (Tahap 2) Pre-Test Machine Learning Dasar": ["Machine Learning"],
    "Bangkit 2024 ILT Quiz - Cloud Computing": ["Cloud Computing"],
    "Bangkit 2024 ILT Quiz - Machine Learning": ["Machine Learning"],
    "Bangkit 2024 ILT Quiz - Mobile Development": ["Mobile Development"],
    "Bangkit 2024 ILT Quiz - Soft Skill": ["Soft Skills"],
    "Bangkit Application Screening 2021": ["General Programming"],
    "Bangkit General Assessment 2022": ["General Programming"],
    "Bangkit General Assessment 2023": ["General Programming"],
    "Bangkit Machine Learning Assessment 2024 Batch 2": ["Machine Learning"],
    "Belajar Android Jetpack Pro": ["Android", "Kotlin", "Jetpack"],
    "Belajar Dasar Git dengan GitHub": ["Git", "GitHub", "DevOps"],
    "Belajar Dasar Manajemen Proyek": ["Project Management"],
    "Belajar Dasar UX Design": ["UX Design", "UI/UX"],
    "Belajar Dasar Visualisasi Data": ["Data Visualization", "Data Analysis"],
    "Belajar Dasar-Dasar Azure Cloud": ["Azure", "Cloud Computing"],
    "Belajar Membangun Aplikasi dengan Universal Windows Platform": ["Windows Development", "C#"],
    "Belajar Membangun LINE Front-end Framework (LIFF)": ["LIFF", "Frontend", "Web"],
    "Belajar Membuat Aplikasi Android dengan Jetpack Compose": ["Android", "Jetpack Compose", "Kotlin"],
    "Belajar Membuat Aplikasi Back-End untuk Pemula dengan Google Cloud": ["Backend", "Google Cloud", "Java"],
    "Belajar Membuat Aplikasi Kognitif": ["AI", "Cognitive Services"],
    "Belajar Membuat Augmented Reality": ["AR", "Unity"],
    "Belajar Membuat Augmented Reality dengan Lens Studio": ["AR", "Lens Studio"],
    "Belajar Membuat Mixed Reality": ["MR", "Unity"],
    "Belajar Penerapan Data Science dengan Microsoft Fabric": ["Data Science", "Microsoft Fabric"],
    "Belajar Penggunaan Generative AI": ["Generative AI", "Prompt Engineering"],
    "Evaluasi Penguasaan Machine Learning": ["Machine Learning"],
    "Exam Challenge Campaign Hari Pendidikan": ["General Knowledge"],
    "Financial Literacy 101": ["Financial Literacy"],
    "Kotlin Android Developer Expert": ["Kotlin", "Android", "Mobile Development"],
    "Membangun Aplikasi Gen AI dengan Microsoft Azure": ["Generative AI", "Azure", "AI"],
    "Memulai Dasar Pemrograman untuk Menjadi Pengembang Software": ["Software Engineering", "Logic"],
    "Memulai Pemrograman Dengan C": ["C", "Programming Basics"],
    "Memulai Pemrograman Dengan Java": ["Java", "Programming Basics"],
    "Memulai Pemrograman dengan Haskell": ["Haskell", "Functional Programming"],
    "Meniti Karier sebagai Software Developer": ["Career Development"],
    "Menjadi AWS Solutions Architect Associate": ["AWS", "Cloud Architecture"],
    "Menjadi Azure Cloud Developer": ["Azure", "Cloud Development"],
    "Pengenalan Data pada Pemrograman (Data 101)": ["Data Basics"],
    "Pengenalan ke Logika Pemrograman (Programming Logic 101)": ["Logic", "Programming Basics"],
    "Pre-Test Dicoding Bootcamp": ["General Programming"],
    "SIB 3 ILT Quiz Machine Learning - Front End": ["Machine Learning", "Frontend"],
    "Simulasi Ujian Associate Android Developer": ["Android"],
    "Simulasi Ujian Associate Cloud Engineer": ["Cloud Computing"],
    "Simulasi Ujian Pendidik Level 1 (Google Certified Educator Level 1 - Indonesian)": ["Education Technology"],
    "Simulasi Ujian TensorFlow Developer Certificate": ["TensorFlow", "Machine Learning"],
    "Source Code Management untuk Pemula": ["Git", "SCM"],
    "Tes Seleksi Asah 2025 - FEBE AI dan REBE AI": ["AI", "Web Development"],
    "Tes Seleksi Laskar AI": ["AI"],
    "Tes Seleksi Offline Training - AI Connect Academy": ["AI"]
}

# Skill proficiency levels based on course progress
SKILL_PROFICIENCY_LEVELS = {
    0: "Pemula",
    25: "Dasar",
    50: "Menengah",
    75: "Mahir",
    100: "Expert"
}


def get_skill_proficiency_label(percentage: int) -> str:
    """Convert percentage to proficiency level label."""
    if percentage < 25:
        return "Pemula"
    elif percentage < 50:
        return "Dasar"
    elif percentage < 75:
        return "Menengah"
    elif percentage < 100:
        return "Mahir"
    else:
        return "Expert"


def get_user_skills_development(user_email: str) -> Dict:
    """
    Analyze user's skill development based on courses taken.
    Returns dummy data mapped to actual course progress.
    """
    data = load_all_data()
    sp = data.get("student_progress", pd.DataFrame())
    
    if sp.empty:
        return {
            "user_email": user_email,
            "skills": [],
            "most_developed": None,
            "top_skills": []
        }
    
    # Get user's courses
    user_email_clean = user_email.strip().lower()
    user_rows = sp[sp['email'].astype(str).str.strip().str.lower() == user_email_clean]
    
    if user_rows.empty:
        return {
            "user_email": user_email,
            "skills": [],
            "most_developed": None,
            "top_skills": []
        }
    
    # Aggregate skill proficiency from courses
    skill_proficiency = {}
    course_count = 0
    
    for _, row in user_rows.iterrows():
        course_name = str(row.get('course_name', '')).strip()
        
        # Get skills from course mapping
        course_skills = COURSE_SKILL_MAP.get(course_name, [])
        
        # Calculate course progress percentage
        try:
            active = float(row.get('active_tutorials', 1)) or 1
            completed = float(row.get('completed_tutorials', 0)) or 0
            
            # Check for NaN and replace with defaults
            if pd.isna(active):
                active = 1
            if pd.isna(completed):
                completed = 0
            
            active = max(float(active), 1)
            completed = max(float(completed), 0)
            
            progress_pct = min(int((completed / active) * 100), 100) if active > 0 else 0
        except Exception:
            progress_pct = 0
        
        # If course completed/graduated, set to 100%
        is_graduated = str(row.get('is_graduated')) == "1"
        if is_graduated:
            progress_pct = 100
        
        course_count += 1
        
        # Aggregate skills
        for skill in course_skills:
            if skill not in skill_proficiency:
                skill_proficiency[skill] = {
                    "proficiency": 0,
                    "courses": [],
                    "progress_percentage": 0
                }
            
            # Average proficiency across courses (weighted)
            current = skill_proficiency[skill]["proficiency"]
            new_proficiency = int((float(current) + float(progress_pct)) / 2)
            skill_proficiency[skill]["proficiency"] = new_proficiency
            skill_proficiency[skill]["progress_percentage"] = progress_pct
            skill_proficiency[skill]["courses"].append({
                "course_name": course_name,
                "progress": progress_pct,
                "status": "Lulus" if is_graduated else "Sedang Dipelajari"
            })
    
    # Convert to list and sort by proficiency
    skills_list = []
    for skill, data in skill_proficiency.items():
        try:
            prof_val = data.get("proficiency", 0)
            # Ensure it's an integer and handle NaN
            if pd.isna(prof_val):
                proficiency = 0
            else:
                proficiency = int(prof_val)
            
            skills_list.append({
                "skill": skill,
                "proficiency": proficiency,
                "proficiency_label": get_skill_proficiency_label(proficiency),
                "courses": data.get("courses", [])
            })
        except Exception as e:
            log.warning("Error processing skill %s: %s", skill, e)
            continue
    
    skills_list.sort(key=lambda x: x["proficiency"], reverse=True)
    
    most_developed = skills_list[0] if skills_list else None
    top_skills = skills_list[:5]  # Top 5 skills
    
    return {
        "user_email": user_email,
        "total_courses": course_count,
        "skills": skills_list,
        "most_developed": most_developed,
        "top_skills": top_skills
    }
