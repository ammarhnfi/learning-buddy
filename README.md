# Learning Buddy 🎓🤖

**Learning Buddy** adalah asisten belajar berbasis AI yang dirancang untuk membantu siswa Dicoding Academy dalam melacak progres, mendapatkan rekomendasi kursus yang personal, dan menganalisis perkembangan skill mereka.

Aplikasi ini menggabungkan antarmuka frontend yang modern (React + Vite) dengan backend cerdas (FastAPI + Google Gemini) yang dilengkapi kemampuan RAG (Retrieval-Augmented Generation) untuk menjawab pertanyaan seputar kurikulum dan progres belajar secara akurat.

## 🌟 Fitur Utama

- **💬 AI Chatbot Pintar**:
  - Menjawab pertanyaan seputar progres belajar ("Sampai mana saya belajar?").
  - Memberikan **Rangkuman Hasil Belajar** yang komprehensif.
  - Menganalisis **Skill Weakness & Strength** (Kuantitatif & Kualitatif).
  - Memberikan rekomendasi kursus selanjutnya berdasarkan level user.
  - Mendukung *fallback* otomatis ke dokumen kurikulum (RAG) jika pertanyaan bersifat umum.

- **🗺️ Interactive Roadmap**:
  - Visualisasi jalur belajar menggunakan `React Flow`.
  - Menampilkan status kelulusan setiap kursus.

- **📊 Dashboard Analisis**:
  - Grafik perkembangan skill (Radar Chart & Bar Chart).
  - Statistik ringkas kursus aktif dan yang telah diselesaikan.

- **📚 Course Catalog**:
  - Daftar lengkap kursus dengan fitur pencarian dan filter.
  - Detail mendalam untuk setiap kursus (Silabus, Teknologi, Kesulitan).

## 🛠️ Tech Stack

### Frontend (`frontend_fix/`)
- **Framework**: React.js (Vite)
- **Styling**: Tailwind CSS
- **Visualisasi**: Recharts (Grafik), React Flow (Roadmap)
- **Icons**: Lucide React

### Backend (`backend_fix/`)
- **Framework**: FastAPI
- **AI/LLM**: Google Gemini (via `google-generativeai`)
- **Data Processing**: Pandas, NumPy, Scikit-learn (TF-IDF/Cosine Similarity)
- **Search**: RAG (Vector Search sederhana dengan caching)
- **Matching Tools**: RapidFuzz (untuk pencocokan nama kursus yang robust)

## 📂 Struktur Project

```
Projek_Learning_Buddy/
├── backend_fix/            # Backend Server (FastAPI)
│   ├── app/
│   │   ├── routers/        # Endpoint API (Chat, Courses, Dashboard)
│   │   ├── services/       # Business Logic (RAG, Roadmap, Skill Analysis)
│   │   ├── utils/          # Data Loading & Helper
│   │   └── core/           # Konfigurasi & Gemini Client
│   ├── data/               # File CSV dataset (Courses, StudentProgress, dll)
│   └── main.py             # Entry point aplikasi
├── frontend_fix/           # Frontend Client (React)
│   ├── src/
│   │   ├── components/     # UI Components Reusable
│   │   ├── pages/          # Halaman Utama (Chat, Dashboard, Roadmap)
│   │   └── services/       # API Client (Axios)
│   └── package.json
└── README.md               # Dokumentasi Proyek
```

## 🚀 Cara Menjalankan Project

### Prasyarat
- **Python 3.10+**
- **Node.js 18+**
- **Google Gemini API Key** (Dapatkan di [Google AI Studio](https://makersuite.google.com/app/apikey))

### 1. Setup Backend
Masuk ke direktori backend :
```bash
cd backend_fix
```

Install dependencies:
```bash
pip install -r requirements.txt
pip install rapidfuzz  # Dependency tambahan untuk matching
```

Buat file `.env` di dalam folder `backend_fix` dan isi dengan API Key Anda:
```env
GEMINI_API_KEY=isi_api_key_disini
```

Jalankan server:
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
*Backend akan berjalan di `http://127.0.0.1:8000`*

### 2. Setup Frontend
Buka terminal baru dan masuk ke direktori frontend:
```bash
cd frontend_fix
```

Install dependencies:
```bash
npm install
```

Jalankan development server:
```bash
npm run dev
```
*Frontend akan berjalan di `http://localhost:5173` (atau port lain yang tersedia)*

## 🧪 Pengujian Chatbot
Cobalah tanyakan hal-hal berikut kepada bot:
1. **"Rangkum hasil belajar saya"** -> Akan menampilkan laporan lengkap kursus & skill.
2. **"Skill apa yang paling berkembang?"** -> Menampilkan data skill spesifik.
3. **"Saya harus belajar apa selanjutnya?"** -> Memberikan rekomendasi roadmap.
4. **"Jelaskan tentang kelas Machine Learning Terapan"** -> Mencari info dari silabus (RAG).

## 📝 Catatan Penting
- Pastikan folder `data/` di backend berisi file CSV yang valid (`Courses_clean.csv`, `StudentProgress_clean.csv`, dll).
- Backend menggunakan *in-memory caching* untuk vector store agar performa pencarian lebih cepat.

---
**Learning Buddy Team** © 2025
