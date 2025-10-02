# 🎙️ Audio NLP API

A FastAPI-based service for audio transcription and NLP processing.

---

## 🚀 Features
- Health check endpoint (`/health`)
- Audio processing pipeline (to be implemented)
- CI/CD with GitHub Actions to be implemented
- Docker to be implemented

---

## 📦 Requirements

- Python 3.11+
- Virtual environment (`venv`)
- Dependencies listed in `requirements.txt`

---

## ⚙️ Setup


```bash
# 1. Clone the repository
git clone https://github.com/meda840/audio-nlp-api.git
cd audio-nlp-api

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate   # On Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

---

## ▶️ Running the API

```bash
# 4. Running the API

uvicorn main:app --reload

