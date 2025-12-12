# Deployment ke Hugging Face Spaces

Guide lengkap untuk deploy Learning Buddy ke Hugging Face Spaces.

## Opsi Deployment

Anda punya beberapa pilihan:

| Opsi | Backend | Frontend | Kelebihan | Kekurangan |
|------|---------|----------|----------|-----------|
| **Docker (Recommended)** | Docker (FastAPI) | Embedded/Static | Full control, flexible | Perlu manage Dockerfile |
| **Streamlit** | Wrapper Streamlit | Built-in UI | Instant deploy, no config | Limited customization |
| **Separate** | HF Spaces Docker | Vercel/Netlify | Best performance | Multiple deployments |

---

## Opsi 1: Deploy Backend FastAPI dengan Docker (Recommended)

### Langkah 1: Setup Hugging Face Account & Create Space

1. Buka https://huggingface.co/spaces
2. Click **"Create new Space"**
3. Isi:
   - **Owner**: Pilih username Anda
   - **Space name**: `learning-buddy` (atau nama lain)
   - **License**: Pilih (Apache 2.0 recommended)
   - **Space SDK**: `Docker`
4. Click **"Create Space"**

### Langkah 2: Persiapkan Backend untuk HF Spaces

Buat file `Dockerfile` di folder root `backend_fix/`:

```dockerfile
# backend_fix/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy aplikasi
COPY app/ ./app
COPY data/ ./data
COPY generate_vectors.py .

# Build embeddings jika belum ada
RUN python generate_vectors.py || echo "Embeddings already exist"

# Expose port
EXPOSE 7860

# Run dengan host 0.0.0.0 agar accessible dari outside
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

**Catatan**: 
- HF Spaces menggunakan port **7860** (bukan 8000)
- Host harus `0.0.0.0` agar accessible

### Langkah 3: Update CORS di Backend

Edit [backend_fix/app/main.py](backend_fix/app/main.py), pastikan CORS config fleksibel:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow semua origin untuk Spaces
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Langkah 4: Push ke HF Spaces

Setelah membuat Space, Anda akan dapat instructions untuk push:

```bash
# Clone space repository
git clone https://huggingface.co/spaces/YOUR_USERNAME/learning-buddy
cd learning-buddy

# Copy semua backend files
cp -r ../backend_fix/* .

# Add requirements.txt (jika belum ada)
# (pastikan sudah ada di backend_fix/)

# Git operations
git add .
git commit -m "Initial commit: Learning Buddy backend"
git push
```

HF Spaces akan otomatis build Docker dan deploy. Tunggu ~5-10 menit.

**Akses Backend**: `https://huggingface.co/spaces/YOUR_USERNAME/learning-buddy`

---

## Opsi 2: Deploy Frontend React (Static)

Setelah build frontend:

```bash
cd frontend_fix
npm run build
# Hasilnya ada di folder 'dist/'
```

### Opsi 2a: Host di Vercel (Recommended untuk React)

```bash
# Install Vercel CLI (jika belum)
npm install -g vercel

# Deploy
cd frontend_fix
vercel
# Ikuti instruksi interaktif
```

### Opsi 2b: Host di GitHub Pages

```bash
# Update vite.config.js
# Tambahkan:
# base: '/Learning-Buddy/'  # jika repo name adalah Learning-Buddy

npm run build

# Push dist/ ke gh-pages branch
git subtree push --prefix frontend_fix/dist origin gh-pages
```

### Opsi 2c: Host Static Files di HF Spaces

Buat folder `frontend_fix/dist/` hasil build, kemudian:

```bash
# Di dalam space repository
cp -r ../frontend_fix/dist/* ./

git add .
git commit -m "Add frontend static files"
git push
```

---

## Opsi 3: All-in-One dengan Streamlit (Simplest)

Jika ingin deployment super cepat, gunakan Streamlit wrapper:

### Buat `app.py` di space:

```python
# app.py
import streamlit as st
import requests
import json

st.set_page_config(page_title="Learning Buddy", layout="wide")

# Theme toggle
if "theme" not in st.session_state:
    st.session_state.theme = "light"

st.title("🤖 Learning Buddy")
st.write("Asisten belajar berbasis AI dengan RAG dan analisis kelemahan skill")

# User selector
user_email = st.text_input(
    "Email User (untuk konteks progress/rekomendasi):",
    value="dina.wijaya1@example.com"
)

# Chat interface
st.subheader("💬 Chat")
question = st.text_area("Tanyakan sesuatu:")

if st.button("Kirim"):
    if question:
        with st.spinner("Loading..."):
            try:
                # Call FastAPI backend (Docker space)
                response = requests.post(
                    "http://localhost:7860/chat/ask",  # Lokal
                    json={
                        "question": question,
                        "user_email": user_email
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.success("✅ Response")
                    st.write(data.get("answer", "No answer"))
                    st.json(data)
                else:
                    st.error(f"Error: {response.status_code}")
            except Exception as e:
                st.error(f"Connection error: {str(e)}")

# Recommendations
st.subheader("📚 Rekomendasi Course")
if st.button("Get Recommendations"):
    with st.spinner("Loading..."):
        try:
            response = requests.get(
                f"http://localhost:7860/recommend/smart/{user_email}"
            )
            if response.status_code == 200:
                recommendations = response.json()
                st.json(recommendations)
            else:
                st.error("Could not fetch recommendations")
        except Exception as e:
            st.error(f"Error: {str(e)}")
```

Deploy ke HF Spaces dengan `app.py` ini:

```bash
git clone https://huggingface.co/spaces/YOUR_USERNAME/learning-buddy
cd learning-buddy

# Copy app.py dan requirements untuk Streamlit
cp ../app.py .
echo "streamlit
requests
python-dotenv" > requirements.txt

git add .
git commit -m "Streamlit wrapper for Learning Buddy"
git push
```

---

## Opsi 4: Recommended Architecture (Best Practice)

**Separate deployments untuk optimal performance:**

```
┌─────────────────────────────────────────┐
│     Frontend (React + Vite)             │
│     → Vercel / Netlify / GH Pages      │
│     https://learning-buddy.vercel.app   │
└──────────────┬──────────────────────────┘
               │ API calls
               ↓
┌─────────────────────────────────────────┐
│     Backend (FastAPI + Docker)          │
│     → HF Spaces                         │
│     https://learning-buddy-hf.spaces    │
└─────────────────────────────────────────┘
```

### Setup untuk Opsi 4:

#### A. Deploy Backend ke HF Spaces Docker

Ikuti Opsi 1 di atas.

#### B. Update Frontend API Endpoint

Edit [frontend_fix/src/services/api.js](frontend_fix/src/services/api.js):

```javascript
// src/services/api.js
const API_BASE = import.meta.env.VITE_API_URL || 
                 'https://YOUR_USERNAME-learning-buddy.hf.space';

// Update semua endpoint
const client = axios.create({
    baseURL: API_BASE,
    timeout: 30000,
});

// ... rest of the code
```

#### C. Update Environment Variables

Buat `.env` di `frontend_fix/`:

```env
VITE_API_URL=https://YOUR_USERNAME-learning-buddy.hf.space
VITE_BACKEND_URL=https://YOUR_USERNAME-learning-buddy.hf.space
```

#### D. Deploy Frontend ke Vercel

```bash
cd frontend_fix
vercel
```

---

## Environment Variables di HF Spaces

### Untuk Docker Backend Space:

1. Buka Space settings
2. Pilih **"Repository secrets"** (atau **"Secrets and tokens"**)
3. Tambahkan:

```
GEMINI_API_KEY=your_actual_api_key
DEBUG=False
FRONTEND_URL=https://your-frontend-domain.vercel.app
```

HF Spaces akan auto-load `.env` dari secrets.

---

## Troubleshooting

| Issue | Solusi |
|-------|--------|
| Port error (address already in use) | Pastikan gunakan port `7860` di Dockerfile |
| CORS error | Pastikan `allow_origins=["*"]` di FastAPI CORS config |
| Embeddings tidak load | Jalankan `python generate_vectors.py` sebelum build Docker |
| Timeout 504 | Kurangi timeout atau optimize embedding loading |
| Frontend tidak bisa akses backend | Cek URL domain dan CORS headers |

---

## Perbandingan Opsi Deployment

### Opsi 1: Docker Backend (Recommended)
```
Setup: Sedang
Cost: Gratis (HF Spaces)
Performance: ⭐⭐⭐⭐
Flexibility: ⭐⭐⭐⭐⭐
Waktu Deploy: 5-10 menit
```

### Opsi 2a: Frontend di Vercel
```
Setup: Mudah
Cost: Gratis (free tier)
Performance: ⭐⭐⭐⭐⭐ (excellent)
Flexibility: ⭐⭐⭐⭐
Waktu Deploy: 1-2 menit
```

### Opsi 3: Streamlit (All-in-One)
```
Setup: Sangat mudah
Cost: Gratis (HF Spaces)
Performance: ⭐⭐⭐
Flexibility: ⭐⭐
Waktu Deploy: 2 menit
Catatan: Cocok untuk MVP/demo
```

---

## Recommended Workflow

### Untuk Development:
```bash
# Terminal 1: Backend
cd backend_fix
.venv\Scripts\activate
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend_fix
npm run dev
```

### Untuk Production (HF Spaces):

1. **Backend**:
   ```bash
   git clone https://huggingface.co/spaces/USERNAME/learning-buddy
   cp backend_fix/* .
   git push
   # HF Spaces auto-build
   ```

2. **Frontend** (di Vercel):
   ```bash
   cd frontend_fix
   vercel
   ```

3. **Update API URL** di frontend ke HF Spaces domain

---

## Monitoring & Logs

### HF Spaces Backend Logs:
- Buka space Anda
- Click **"Logs"** tab
- Real-time streaming logs

### Check Health:
```bash
curl https://YOUR_USERNAME-learning-buddy.hf.space/

# Response: {"status": "ok"}
```

### Check API Docs:
```
https://YOUR_USERNAME-learning-buddy.hf.space/docs
```

---

## Tips & Best Practices

✅ **Do's:**
- Gunakan Docker untuk full control
- Separate frontend & backend untuk scalability
- Implement proper error handling & logging
- Cache embeddings untuk performance
- Use secrets untuk API keys (jangan hardcode)

❌ **Don'ts:**
- Jangan commit API keys ke Git
- Jangan gunakan `localhost` di Dockerfile
- Jangan set `DEBUG=True` di production
- Jangan forget update CORS origins

---

## Resources

- **HF Spaces Docs**: https://huggingface.co/docs/hub/spaces
- **Vercel Docs**: https://vercel.com/docs
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/
- **Docker Docs**: https://docs.docker.com/

---

## Next Steps

1. **Buat HF Account**: https://huggingface.co/join
2. **Create Space**: https://huggingface.co/spaces/create
3. **Setup Docker** (Opsi 1) atau **Streamlit** (Opsi 3)
4. **Push ke Spaces**
5. **Test via API Docs** atau **frontend**
6. **Monitor logs** dan **debug**

Siap deploy! 🚀
