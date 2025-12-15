def analyze_skill_weakness(progress: dict):
    """
    Menganalisis kelemahan skill berdasarkan data progres:
    - submission_rating (0–100)
    - exam_score (0–100)
    - perbandingan completed vs active
    """

    completed = int(progress.get("completed_tutorials") or 0)
    active = int(progress.get("active_tutorials") or 0)
    submission_rating = float(progress.get("submission_rating") or 0)
    exam_score = float(progress.get("exam_score") or 0)

    findings = []
    suggestions = []

    # --- 1. Analisis mastery berdasarkan nilai ujian ---
    if exam_score < 60:
        findings.append("Pemahaman konsep dasar masih lemah (nilai ujian rendah).")
        suggestions.append("Pelajari ulang modul fundamental dan kerjakan latihan soal tambahan.")

    elif exam_score < 80:
        findings.append("Masih ada beberapa konsep yang belum kuat.")
        suggestions.append("Perbanyak latihan mandiri dan ulangi kuis modul tertentu.")

    else:
        findings.append("Pemahaman konsep cukup baik.")
        suggestions.append("Lanjutkan ke materi lanjutan untuk memperdalam skill.")

    # --- 2. Analisis skill praktikal berdasarkan submission rating ---
    if submission_rating < 60:
        findings.append("Skill praktikal (proyek/implementasi) masih lemah.")
        suggestions.append("Coba buat mini–project untuk meningkatkan kemampuan praktikal.")

    elif submission_rating < 80:
        findings.append("Implementasi masih perlu diperkuat.")
        suggestions.append("Review kembali hasil tugas yang kurang dan coba perbaiki.")

    # --- 3. Analisis konsistensi belajar ---
    total = max(completed + active, 1)
    completion_ratio = completed / total

    if completion_ratio < 0.4:
        findings.append("Konsistensi penyelesaian modul rendah.")
        suggestions.append("Buat jadwal belajar mingguan untuk meningkatkan ritme belajar.")

    elif completion_ratio < 0.7:
        findings.append("Perlu meningkatkan komitmen penyelesaian modul.")
        suggestions.append("Targetkan 2–3 modul per minggu untuk mempercepat progres.")

    weakness_level = (
        "Signifikan" if exam_score < 60 or submission_rating < 60 else
        "Moderate" if exam_score < 80 or submission_rating < 80 else
        "Ringan"
    )

    return {
        "weakness_level": weakness_level,
        "findings": findings,
        "suggestions": suggestions
    }
