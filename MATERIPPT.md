# Materi Presentasi: Learning Buddy (AI-Powered Student Assistant)

---

## 1. Latar Belakang

### Tinjauan & Tren Terkini
Dunia pendidikan sedang mengalami transformasi digital masif (*EdTech*). Tren terkini menunjukkan pergeseran dari **Learning Management Systems (LMS)** konvensional yang statis menuju **AI-Driven Personalized Learning**. Studi menunjukkan bahwa siswa dalam pembelajaran mandiri (self-paced learning) sering mengalami penurunan motivasi karena kurangnya umpan balik yang personal dan instan.

### Identifikasi Kesenjangan (Gap Analysis)
Kebanyakan platform kursus online saat ini (seperti Dicoding, Coursera, dll) sangat baik dalam menyediakan konten materi, namun masih kurang dalam hal **pendampingan personal**. Siswa sering merasa "tersesat" di tengah banyaknya materi tanpa tahu:
1.  Apakah mereka sudah di jalur yang benar?
2.  Apa kelemahan spesifik mereka?
3.  Langkah konkret apa yang harus diambil selanjutnya?

Adanya kesenjangan antara "materi yang tersedia" dan "bimbingan yang dibutuhkan" inilah yang menjadi dasar pengembangan **Learning Buddy**.

---

## 2. Alasan & Rumusan Masalah

### Mengapa memilih tema ini?
Kami melihat tingginya tingkat *drop-out* pada kursus online bukan karena materinya sulit, melainkan karena siswa kehilangan arah. Kami ingin memecahkan masalah ini dengan teknologi Generative AI yang kini sudah matang dan terjangkau.

### Masalah yang ingin diselesaikan
1.  **Informasi Terfragmentasi**: Data progres, nilai, dan saran perbaikan sering tersebar di berbagai menu dan sulit dipahami siswa.
2.  **Kurangnya Personalisasi**: Rekomendasi kursus seringkali *generic* (sama untuk semua orang), tidak berbasis data skill aktual siswa.
3.  **Kebingungan Roadmap**: Siswa pemula sering tidak tahu urutan belajar yang optimal untuk mencapai karir tertentu.

---

## 3. Perbandingan dengan Aplikasi Serupa

### Produk Sejenis (Existing Solutions)
Kebanyakan LMS hanya memiliki "Dashboard Progress" standar yang menampilkan *progress bar* (0-100%).
*   **Kekurangan**: Hanya menampilkan angka kuantitatif. Tidak ada penjelasan kualitatif ("Mengapa nilai saya rendah di modul ini?").
*   **Kekurangan**: Fitur pencarian bantuan biasanya hanya berupa FAQ statis.

### Keunggulan Learning Buddy (Value Proposition)
Perbedaan utama Learning Buddy dibanding dashboard LMS biasa:
1.  **Interaktif**: Bukan sekadar melihat grafik, siswa bisa **bertanya** kepada *Personal Assistant* tentang progres mereka ("Apa yang harus saya perbaiki?").
2.  **Qualitative Insight**: Menggabungkan data angka (nilai ujian) dengan analisis AI untuk memberikan saran verbal yang memotivasi.
3.  **Context-Aware**: Chatbot 'tahu' siapa siswa tersebut, kursus apa yang diambil, dan riwayat nilainya, sehingga jawaban sangat spesifik (bukan jawaban robot umum).

---

## 4. Hasil Pengembangan Produk

### Fitur Utama & Peningkatan
Kami telah mengembangkan sistem **End-to-End** yang terdiri dari:
1.  **Backend Cerdas (FastAPI + RAG)**:
    *   Sistem **Intent Recognition** baru yang membedakan pertanyaan *Summary*, *Skill*, atau *Rekomendasi*.
    *   Integrasi **RapidFuzz** untuk pencocokan nama kursus yang toleran terhadap *typo*.
2.  **Frontend Interaktif (React)**:
    *   Dashboard visual dengan grafik skill.
    *   Roadmap interaktif berbasis node.

### Mockup & Hasil (Screenshot Placeholder)
*   *Screenshot 1: Halaman Chatbot memberikan "Rangkuman Hasil Belajar" yang personal.*
*   *Screenshot 2: Visualisasi Skill Chart yang menunjukkan kekuatan vs kelemahan.*

### Mengapa Implementasi Ini Dipilih?
*   **Tech Stack (React + FastAPI)**: Kombinasi performa tinggi dan kemudahan pengembangan fitur AI.
*   **RAG (Retrieval-Augmented Generation)**: Dipilih untuk mencegah halusinasi AI. Bot hanya menjawab berdasarkan silabus resmi, bukan mengarang materi.
*   **Separation of Concerns**: Memisahkan *logic* rekomendasi dan *interface* chat agar sistem mudah dikembangkan (misal: ganti model AI tanpa ubah UI).

---

## 5. Dokumentasi

Seluruh kode sumber, cara instalasi, dan panduan penggunaan telah didokumentasikan secara lengkap dalam file `README.md` di repositori proyek.
*   **Akses Dokumen**: Silakan merujuk ke file `README.md` di root folder.
*   **Replikasi**: Instruksi `pip install` dan `npm run dev` sudah tersedia untuk dicoba di lokal.

---

## 6. Rencana Implementasi Lokal (Strategi 3 Bulan)

### Bulan 1: Stabilisasi & Beta Testing
*   **Timeline**: Minggu 1-4.
*   **Resource**: 1 Backend Dev, 1 Frontend Dev.
*   **Fokus**: Memperbaiki *bug* kecil pada integrasi RAG dan mengoptimalkan latensi respon chatbot (target < 3 detik).
*   **Budget**: Server Cloud kecil (biaya ~$20/bulan) untuk hosting demo.

### Bulan 2: Integrasi Database & Gamifikasi
*   **Timeline**: Minggu 5-8.
*   **Resource**: +1 Database Engineer.
*   **Fokus**: Migrasi dari CSV ke PostgreSQL agar data *real-time*. Menambahkan fitur *Badges* (lencana) saat siswa mencapai skill tertentu.
*   **Alat**: Database Migration Tools, Supabase/Firebase.

### Bulan 3: Peluncuran & Mobile Support
*   **Timeline**: Minggu 9-12.
*   **Fokus**: Membuat tampilan responsif penuh (PWA) agar bisa diakses nyaman via HP. Rilis versi 1.0 untuk digunakan siswa internal.
*   **Budget Langganan**: Estimasi biaya API Google Gemini (tergantung *traffic* user).
