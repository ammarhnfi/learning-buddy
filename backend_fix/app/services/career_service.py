# app/services/career_service.py
from typing import List, Dict

# Defined Career Profiles and their required skills (weighted)
CAREER_PROFILES = [
    {
        "role": "Android Developer",
        "description": "Building mobile applications for the Android ecosystem.",
        "required_skills": ["Android", "Kotlin", "Java", "Mobile Development", "Jetpack"],
        "min_proficiency": 25 # Minimum proficiency to be considered "matched"
    },
    {
        "role": "iOS Developer",
        "description": "Creating premium apps for Apple's iOS platform.",
        "required_skills": ["Swift", "iOS", "Mobile Development"],
        "min_proficiency": 25
    },
    {
        "role": "Front-End Web Developer",
        "description": "Crafting beautiful and interactive user interfaces for the web.",
        "required_skills": ["Frontend", "Web", "HTML", "CSS", "JavaScript", "ReactJS"],
        "min_proficiency": 25
    },
    {
        "role": "Back-End Developer",
        "description": "Building robust server-side logic and APIs.",
        "required_skills": ["Backend", "Node.js", "Python", "Database", "API", "SQL", "JavaScript"],
        "min_proficiency": 25
    },
    {
        "role": "Cloud Engineer",
        "description": "Designing and managing scalable cloud infrastructure.",
        "required_skills": ["Cloud Computing", "AWS", "Google Cloud", "Azure", "DevOps"],
        "min_proficiency": 25
    },
    {
        "role": "Data Scientist",
        "description": "Analyzing complex data to drive decision making.",
        "required_skills": ["Data Science", "Python", "Machine Learning", "Data Analysis", "Statistics", "SQL"],
        "min_proficiency": 25
    },
    {
        "role": "Machine Learning Engineer",
        "description": "Building and deploying AI models.",
        "required_skills": ["Machine Learning", "Deep Learning", "Python", "TensorFlow", "AI"],
        "min_proficiency": 25
    },
     {
        "role": "Multi-Platform App Developer",
        "description": "Building apps for both iOS and Android with a single codebase.",
        "required_skills": ["Flutter", "Dart", "Mobile Development"],
        "min_proficiency": 25
    }
]

def match_career(user_skills: List[Dict]) -> List[Dict]:
    """
    Match user skills to career profiles.
    
    Args:
        user_skills: List of dicts, e.g., [{"skill": "Python", "proficiency": 80}, ...]
        
    Returns:
        List of careers with 'match_percentage' sorted descending.
    """
    matches = []
    
    # Create a quick lookup for user proficiency
    user_skill_map = {s["skill"].lower(): s["proficiency"] for s in user_skills}
    
    for profile in CAREER_PROFILES:
        role = profile["role"]
        required = profile["required_skills"]
        
        # Calculate Match Score
        # Logic: Score = (Sum of proficiencies for matching skills / Total max proficiency for all required skills) * 100
        # This is a bit unique. Let's try:
        # Score = (Matches Found / Total Required) * 50 + (Average Proficiency of Matches) * 0.5
        
        matches_found = 0
        total_proficiency_sum = 0
        
        for req_skill in required:
            key = req_skill.lower()
            if key in user_skill_map:
                proficiency = user_skill_map[key]
                if proficiency > 0:
                    matches_found += 1
                    total_proficiency_sum += proficiency
        
        if matches_found == 0:
            continue
            
        # 1. Coverage Score (How many of the required skills do you have?)
        coverage_pct = (matches_found / len(required)) * 100
        
        # 2. Proficiency Score (How good are you at the skills you have?)
        avg_proficiency = total_proficiency_sum / matches_found if matches_found > 0 else 0
        
        # Weighted Final Score: 60% Coverage, 40% Proficiency
        final_score = (coverage_pct * 0.6) + (avg_proficiency * 0.4)
        
        if final_score > 10: # Filter out very low matches
            matches.append({
                "role": role,
                "description": profile["description"],
                "match_score": int(final_score),
                "skills_matched": matches_found,
                "total_skills_required": len(required)
            })
            
    # Sort by score
    matches.sort(key=lambda x: x["match_score"], reverse=True)
    
    return matches
