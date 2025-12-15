# SWOT Analysis: Learning Buddy Project

Analisis ini mengevaluasi posisi strategis proyek **Learning Buddy** berdasarkan arsitektur, fitur, dan potensi pengembangannya.

## 💪 Strengths (Kekuatan)

1.  **Integrasi AI Lanjutan**:
    *   Menggunakan **Google Gemini** untuk pemahaman bahasa alami yang superior.
    *   Implementasi **RAG (Retrieval-Augmented Generation)** membuat chatbot mampu menjawab pertanyaan spesifik tentang kurikulum tanpa halusinasi berlebih.
    *   Fitur **Smart Recommendation** yang menggabungkan analisis level kursus dan minat user.

2.  **Arsitektur Modern & Scalable**:
    *   **Frontend**: React + Vite + Tailwind CSS memberikan performa UI yang sangat cepat dan responsif.
    *   **Backend**: FastAPI adalah framework Python modern yang mendukung proses *asynchronous*, ideal untuk operasi I/O-bound seperti pemanggilan AI API.
    *   **Loose Coupling**: Pemisahan jelas antara logika bisnis (services), API (routers), dan UI (frontend) memudahkan maintenance.

3.  **Personalisasi Pengalaman Belajar**:
    *   Sistem mampu mendeteksi *learning path* pengguna secara otomatis dari data CSV.
    *   Analisis Skill (Kuantitatif & Kualitatif) memberikan nilai tambah nyata bagi siswa untuk mengetahui kelemahan mereka.
    *   **Robust Matching**: Penggunaan `RapidFuzz` memperbaiki masalah umum kesalahan pengetikan nama kursus.

4.  **Visualisasi Data yang Kaya**:
    *   Penggunaan **React Flow** untuk Roadmap dan **Recharts** untuk statistik membuat data progres yang membosankan menjadi menarik dan mudah dipahami.

## ⚠️ Weaknesses (Kelemahan)

1.  **Ketergantungan Data Lokal (CSV)**:
    *   Saat ini sistem masih bergantung pada file CSV statis (`StudentProgress_clean.csv`, dll).
    *   **Risiko**: Sulit untuk melakukan update data *real-time* atau menangani *concurrent writing* jika banyak user mengakses serentak.
    *   **Solusi Sementara**: Cukup untuk prototipe/demo, tapi kurang ideal untuk produksi skala besar.

2.  **Ketergantungan Eksternal (API Key)**:
    *   Fungsionalitas inti (Chatbot, Analisis) mati total jika **Gemini API Key** limit habis atau tidak valid.
    *   Latency respon sangat bergantung pada kecepatan server Google.

3.  **Absennya Sistem Autentikasi Robust**:
    *   Identifikasi user saat ini hanya berbasis pencarian email di CSV. Tidak ada login password atau OAuth yang aman.

## 🚀 Opportunities (Peluang)

1.  **Migrasi ke Database Cloud**:
    *   Mengganti CSV dengan **PostgreSQL** atau **Supabase** akan memungkinkan fitur manajemen user yang nyata, history chat tersimpan, dan update progress real-time.

2.  **Gamifikasi**:
    *   Menambahkan fitur *Badges*, *Leaderboard*, atau *Daily Streak* untuk meningkatkan motivasi belajar siswa (data analytics sudah mendukung ini).

3.  **Ekspansi ke Mobile App**:
    *   Karena menggunakan React, kode frontend bisa cukup mudah diporting ke **React Native** atau dikemas sebagai **PWA (Progressive Web App)** untuk akses mobile yang lebih baik.

4.  **Fitur "Mock Interview" AI**:
    *   Memanfaatkan kemampuan Gemini untuk mensimulasikan sesi wawancara kerja berdasarkan skill user yang sudah terdeteksi "Mahir".

## 🛡️ Threats (Ancaman)

1.  **Biaya Operasional API**:
    *   Jika user base membesar, penggunaan token API LLM akan melonjak. Ketergantungan pada API berbayar (jika free tier habis) bisa menjadi beban biaya.

2.  **Isu Privasi Data**:
    *   Mengirimkan data progres siswa ke API pihak ketiga (Google Gemini) untuk dianalisis perlu pertimbangan privasi dan kepatuhan regulasi data (jika diterapkan secara komersial).

3.  **Perubahan Struktur Data**:
    *   Jika format CSV dari sumber (Dicoding/LMS lain) berubah drastis, `data_loader.py` perlu ditulis ulang, yang berpotensi memutus layanan sementara.
