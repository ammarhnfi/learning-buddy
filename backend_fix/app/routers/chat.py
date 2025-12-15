# app/routers/chat.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Any
import numpy as np
import math
import logging
import traceback
import pandas as pd

from app.core.gemini_client import embed_query, generate_answer
from app.services.rag_service import (
    retrieve_similar,
    get_kb,
    init_kb,
    search_progress_by_email,
    get_course_info,
    get_course_tutorials,
    calculate_remaining_requirements,
)
from app.services.smart_recommender import get_smart_recommendation
from app.services.skill_analyzer import analyze_skill_weakness
from app.services.skill_development_service import get_user_skills_development

# Set up logging
log = logging.getLogger("LearningBuddy.chat")
router = APIRouter()

class AskReq(BaseModel):
    question: str
    top_k: Optional[int] = 3
    user_email: Optional[str] = None  # Primary identifier
    user_name: Optional[str] = None   # Deprecated, kept for backward compatibility
    interests: Optional[str] = None   # Comma-separated interests

def sanitize_for_json(obj: Any) -> Any:
    """
    Recursively replace NaN/Infinity with None for JSON compliance.
    """
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    elif isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(v) for v in obj]
    elif pd.isna(obj):  # Handle numpy/pandas NaN/NaT
        return None
    return obj

def _clean_text(s: str) -> str:
    return (s or "").strip().lower()

def is_summary_question(q: str) -> bool:
    """
    Menangkap pertanyaan ringkasan belajar total.
    """
    q = _clean_text(q)
    keywords = [
        "rangkum", "ringkasan", "summary",
        "hasil belajar", "pencapaian", "report",
        "laporan belajar", "apa saja yang sudah saya pelajari",
        "kesimpulan belajar"
    ]
    return any(k in q for k in keywords)

def is_progress_question(q: str) -> bool:
    q = _clean_text(q)
    keywords = [
        "progress", "progres", "perkembangan belajar",
        "sampai dimana", "sampai di mana",
        "berapa persen", "status belajar",
        "kemajuan belajar", "sampai sejauh",
        # variations for "current course"
        "course saya", "kelas saya", "course yang saya ambil",
        "kelas yang saya ambil", "sedang saya kerjakan",
        "course yang saya kerjakan", "kelas yang saya kerjakan",
        "course apa yang saya kerjakan", "course apa yang saya ambil",
        "kelas apa yang saya ambil", "kelas apa yang saya kerjakan",
    ]
    return any(k in q for k in keywords)

def is_recommendation_question(q: str) -> bool:
    q = _clean_text(q)
    keywords = [
        "rekomendasi", "rekomendasikan", "setelah ini belajar apa",
        "apa yang harus saya pelajari", "next course", "lanjutan dari",
        "course berikutnya", "roadmap belajar", "saran kursus",
        "saran belajar", "apa yang harus dipelajari selanjutnya"
    ]
    return any(k in q for k in keywords)

def is_skill_weakness_question(q: str) -> bool:
    """
    Menangkap pertanyaan seputar skill, baik itu weakness (kelemahan)
    maupun strength (skill yang berkembang).
    """
    q = _clean_text(q)
    keywords = [
        "skill", "kemampuan", "kelemahan", "weakness",
        "apa yang kurang", "apa yang lemah",
        "bagian mana yang kurang", "dimana yang kurang",
        "apa yang harus diperbaiki", "apa yang perlu ditingkatkan",
        "apa yang berkembang", "paling berkembang", "paling jago", 
        "skill saya", "top skill", "kekuatan saya"
    ]
    return any(k in q for k in keywords)

@router.post("/ask")
def ask(req: AskReq):
    q = (req.question or "").strip()
    if not q:
        raise HTTPException(status_code=400, detail="question is required")

    # Prioritize email over name
    user_email = req.user_email or req.user_name
    user_display_name = None
    
    log.info("Incoming ask: user_email=%s question=%s", user_email, q)

    try:
        # --- 1) SMART RECOMMENDATION BRANCH ---
        if user_email and is_recommendation_question(q):
            log.info("Matched branch: SMART RECOMMENDATION for user_email=%s", user_email)
            try:
                interests_list = (
                    [i.strip() for i in req.interests.split(",") if i.strip()]
                    if req.interests else []
                )
                recs = get_smart_recommendation(
                    user_identifier=user_email,
                    interests_override=interests_list,
                    top_n=req.top_k or 5
                )
                
                # Get user name for better UX
                progress = search_progress_by_email(user_email)
                user_display_name = progress.get("name") if progress else user_email
                
                # Format recommendations for LLM context
                rec_text = "\n".join([
                    f"- {r['course_name']} (level {r.get('course_level_str', '?')}, score {r.get('score', 0):.2f}) {r.get('reason','')}"
                    for r in recs
                ])
                
                prompt = f"""
    Anda adalah Learning Buddy. Berikan penjelasan singkat (Bahasa Indonesia) atas rekomendasi berikut untuk {user_display_name}:

    {rec_text}

    Jelaskan alasan singkat tiap rekomendasi. Jika ada alasan spesifik (misal karena interest), sebutkan.
    """
                ans = generate_answer(prompt)
                return sanitize_for_json({
                    "answer": ans,
                    "source": "SmartRecommendation",
                    "user": user_display_name,
                    "user_email": user_email,
                    "recommendations": recs
                })
            except Exception as e:
                log.exception("Smart recommendation branch failed")
                # Fallback to general RAG if rec fails
                pass

        # --- 2) SUMMARY BRANCH (NEW) ---
        if user_email and is_summary_question(q):
            log.info("Matched branch: SUMMARY for user_email=%s", user_email)
            try:
                # Gather all data
                progress = search_progress_by_email(user_email)
                skills_data = get_user_skills_development(user_email)
                
                if not progress:
                    ans = generate_answer(f"Tidak ada data progres untuk email {user_email}.")
                    return sanitize_for_json({"answer": ans, "source": "Summary", "note": "No progress data"})

                user_display_name = progress.get("name")
                
                # Progress Data
                active_course = progress.get("course_name", "-")
                is_graduated = str(progress.get("is_graduated")).strip() == "1"
                status_course = "Selesai" if is_graduated else "Sedang Dipelajari"
                
                # Skill Data
                most_developed = skills_data.get("most_developed")
                most_developed_str = f"{most_developed['skill']} ({most_developed['proficiency_label']} - {most_developed.get('progress_percentage',0)}%)" if most_developed else "Belum terdeteksi"
                
                other_skills_list = skills_data.get("top_skills", [])[1:3]
                other_skills_str = ", ".join([f"{s['skill']} ({s['proficiency_label']})" for s in other_skills_list])
                if not other_skills_str:
                    other_skills_str = "Belum terdeteksi"

                prompt = f"""
    Anda adalah Learning Buddy. Buat Rangkuman Hasil Belajar untuk user.

    DATA USER:
    Nama: {user_display_name}
    Kursus Aktif: {active_course} ({status_course})
    Skill Paling Berkembang: {most_developed_str}
    Skill Lainnya: {other_skills_str}

    INSTRUKSI:
    1. Buat jawaban dengan format terstruktur seperti laporan singkat.
    2. Gunakan poin-poin agar mudah dibaca.
    3. Contoh output yang diharapkan:
    "Halo [Nama], berikut rangkuman hasil belajarmu:
        - Kursus Aktif: [Nama Course] (Status)
        - Skill Paling Berkembang: [Skill]
        - Skill Lainnya: [Skill A], [Skill B]"
    """
                ans = generate_answer(prompt)
                return sanitize_for_json({
                    "answer": ans,
                    "source": "Summary",
                    "user": user_display_name,
                    "data": {
                        "progress": progress,
                        "skills": skills_data
                    }
                })
            except Exception as e:
                log.exception("Summary branch failed")
                pass

        # --- 3) PROGRESS BRANCH ---
        if user_email and is_progress_question(q):
            log.info("Matched branch: PROGRESS for user_email=%s", user_email)
            progress = search_progress_by_email(user_email)
            
            if not progress:
                msg = (
                    f"Halo kak, kami cek email '{user_email}' belum terdaftar di database kami. "
                    "Silakan periksa kembali email yang digunakan."
                )
                return sanitize_for_json({"answer": msg, "source": "Generative", "note": "No progress data"})
            
            user_display_name = progress.get("name")
            course_name = progress.get("course_name")
            
            try:
                active = int(progress.get("active_tutorials") or 0)
                completed = int(progress.get("completed_tutorials") or 0)
                graduated = str(progress.get("is_graduated")).strip().lower() in ("1", "true", "yes")
                
                # Additional Course Info
                course_info = get_course_info(course_name)
                course_tutorials = get_course_tutorials(course_name)
                requirements = calculate_remaining_requirements(progress, course_tutorials)
                
                percent = requirements.get("completion_percentage", 0)
                remaining_tuts = requirements.get("remaining_tutorials", 0)
                total_tuts = requirements.get("total_tutorials", 0)

                # Construct prompt based on status
                if graduated:
                    prompt_text = f"Status: SUDAH LULUS.\nProgress: 100%."
                else:
                    prompt_text = (
                        f"Status: BELUM LULUS.\n"
                        f"Progress: {percent}%\n"
                        f"Completed: {completed} / {total_tuts}\n"
                        f"Sisa Tutorial: {remaining_tuts}\n"
                    )

                prompt = f"""
    Anda adalah Learning Buddy. Jawab singkat, jelas, tidak bertele-tele.
    Nama User: {user_display_name}
    Course Saat Ini: {course_name}
    {prompt_text}
    Difficulty: {course_info.get('course_difficulty', 'N/A')}
    Technologies: {course_info.get('technologies', 'N/A')}

    Instruksi:
    1. Sapa user dengan namanya.
    2. Laporkan status progres mereka.
    3. Berikan semangat atau saran singkat.
    """
                ans = generate_answer(prompt)
                return sanitize_for_json({
                    "answer": ans,
                    "source": "UserProgress",
                    "user": user_display_name,
                    "user_email": user_email,
                    "progress_percent": percent,
                    "course_info": course_info if course_info else None,
                    "remaining": requirements
                })

            except Exception as e:
                log.exception("Progress branch failed")
                # Fallback to RAG
                pass

        # --- 4) SKILL WEAKNESS/STRENGTH BRANCH ---
        if user_email and is_skill_weakness_question(q):
            log.info("Matched branch: SKILL ANALYSIS for user_email=%s", user_email)
            progress = search_progress_by_email(user_email)
            if not progress:
                ans = generate_answer(f"Tidak ada data progres untuk email {user_email}.")
                return sanitize_for_json({"answer": ans, "source": "SkillAnalysis", "note": "No progress data"})

            user_display_name = progress.get("name")
            
            try:
                # 3a. Get Qualitative Analysis (Habits, Scores)
                qualitative_result = analyze_skill_weakness(progress)
                
                # 3b. Get Quantitative Skill Data (Specific Tech Skills)
                tech_skills_data = get_user_skills_development(user_email)
                
                # Extract top developed skill
                most_developed_str = "Belum ada skill spesifik yang terdeteksi."
                if tech_skills_data.get("most_developed"):
                    md = tech_skills_data["most_developed"]
                    most_developed_str = f"{md['skill']} ({md['proficiency_label']} - {md['proficiency']}%)"
                
                # Extract top 3 skills list
                top_skills = tech_skills_data.get("top_skills", [])
                top_skills_str = ", ".join([f"{s['skill']} ({s['proficiency_label']} - {s['proficiency']}%)" for s in top_skills[:3]])

                # Combine into prompt
                prompt = f"""
    Anda adalah Learning Buddy. Jawab pertanyaan user tentang skill mereka dengan kombinasi data kuantitatif dan kualitatif.

    DATA USER:
    Nama: {user_display_name}
    Skill Paling Berkembang (Quantitative): {most_developed_str}
    Top Skills Lainnya: {top_skills_str}

    ANALISIS BELAJAR (Qualitative):
    Weakness Level: {qualitative_result['weakness_level']}
    Temuan (Habits/Scores): {", ".join(qualitative_result['findings'])}
    Saran Perbaikan: {", ".join(qualitative_result['suggestions'])}

    INSTRUKSI:
    1. JIKA user bertanya "Skill apa yang paling berkembang?", JAWAB LANGSUNG dengan menyebutkan Skill Paling Berkembang dari data di atas.
    2. JIKA user bertanya tentang kelemahan, fokus pada bagian ANALISIS BELAJAR.
    3. Gabungkan keduanya secara natural.
    4. Jangan terlalu kaku, gunakan bahasa Indonesia yang luwes dan ramah.

    User Question: "{q}"

    Contoh Jawaban Ideal (jika ditanya skill berkembang):
    "Halo [Nama], Skill yang paling berkembang saat ini adalah **[Skill]** dengan level **[Level]** ([%]%).
    Berdasarkan analisis kami, pemahaman konsepmu sudah cukup baik, namun perlu tingkatkan konsistensi belajarmu."
    """
                ans = generate_answer(prompt)
                return sanitize_for_json({
                    "answer": ans,
                    "source": "SkillAnalysis",
                    "user": user_display_name,
                    "analysis_qualitative": qualitative_result,
                    "skills_quantitative": tech_skills_data
                })
            except Exception as e:
                log.exception("Skill analysis branch failed")
                pass

        # --- 5) RAG / GENERAL FALLBACK ---
        log.info("Falling back to RAG/Generative pipeline for question: %s", q)
        
        # 5a. Init KB if needed
        try:
            init_kb(force_rebuild=False)
        except Exception as e:
            log.warning("KB init warning: %s", e)

        # 5b. Embed & Search
        try:
            q_vec = embed_query(q)
            sims = retrieve_similar(q_vec, top_k=(req.top_k or 3))
        except Exception:
            log.exception("Embedding/Search failed")
            sims = []

        retrieved_text = ""
        top_score = 0.0
        if sims:
            top_idx, top_score = sims[0]
            _, docs = get_kb()
            if top_idx < len(docs):
                retrieved_text = docs[top_idx]

        # Threshold check for RAG context usage
        if top_score >= 0.55 and retrieved_text:
            prompt = f"""
    You are Learning Buddy assistant. Use the following context to answer user accurately.

    CONTEXT:
    {retrieved_text}

    QUESTION:
    {q}

    Answer concisely and in Indonesian.
    """
            try:
                ans = generate_answer(prompt)
                return sanitize_for_json({
                    "answer": ans,
                    "source": "RAG",
                    "score": top_score,
                    "retrieved_doc": retrieved_text
                })
            except Exception:
                log.exception("RAG generation failed")

        # 5c. Pure Generative Fallback
        try:
            # If we have user info but RAG failed, inject brief context
            context_inject = ""
            if user_email:
                # Try to get minimal user name context
                p = search_progress_by_email(user_email)
                if p:
                    context_inject = f"User Name: {p.get('name')}\n"

            prompt = f"""
    You are Learning Buddy. {context_inject}
    The user asked: "{q}"
    Answer as a helpful assistant in Indonesian.
    """
            ans = generate_answer(prompt)
            return sanitize_for_json({"answer": ans, "source": "Generative", "score": None})
        except Exception as e:
            log.exception("Generative LLM failed")
            raise HTTPException(status_code=500, detail="LLM generation failed")
            
    except Exception as e:
        log.exception("Unhandled error in ask endpoint")
        raise HTTPException(status_code=500, detail=str(e))