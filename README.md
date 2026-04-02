# 🏠 Roommate Matching System — Women-Only Personalized Living

> **A smart, AI-powered platform for women to find safe, compatible roommates using a premium Tinder-style interface and Groq LLaMA 3 match analysis.**

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Groq](https://img.shields.io/badge/AI-Groq--LLaMA--3-orange)](https://groq.com)
[![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey?logo=sqlite)](https://sqlite.org)

---

## 📌 About

**Roommate Matching System** is a premium application designed exclusively for women. It moves away from traditional list-based browsing to a modern **Tinder-style swipe experience**, where decisions are based on lifestyle compatibility rather than just photos.

The system uses a **Hybrid Recommendation Engine** + **Groq AI** to provide deep insights into why two users are compatible.

### ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🔥 **Tinder-Style Matching** | A fluid, gesture-based swipe deck for browsing potential roommates (Photos hidden initially for safety/privacy). |
| 🤖 **Groq AI Analysis** | Uses LLaMA 3.1 via Groq to generate "punchy" one-sentence match explanations based on shared lifestyle traits. |
| 📊 **Hybrid Scoring** | Combines Weighted Rule-Based logic (50%) with ML Cosine Similarity (50%) for high-accuracy matching. |
| 📋 **Smart Questionnaire** | A dedicated setup section to define sleep cycles, noise tolerance, and guest policies. |
| 🔐 **Secure Auth** | JWT-based authentication with a professional login overlay. |
| 🌐 **Offline Friendly** | Uses local-first SQLite, making it perfect for regions with restricted Wi-Fi (like college campuses). |
| 🛡️ **Safety Tools** | Identity verification badges, emergency check-ins, and anonymous reporting. |

---

## 🛠️ Technical Architecture

### The Brain (Hybrid Engine)
The engine calculates a score from **1.0 to 10.0** by analyzing:
1.  **Rule-Based (50%)**: Checks strict non-negotiables (Sleep schedule, Guest policy, Noise).
2.  **ML Cosine Similarity (50%)**: Vectors are created from one-hot encoded preferences to find lifestyle "vibe" matches.
3.  **Groq LLM**: Interprets the resulting data to write a human-readable bio for the match card.

### The Stack
- **Backend**: FastAPI (Python), SQLAlchemy (Async), Pydantic v2.
- **Frontend**: Vanilla HTML5, CSS3 (Glassmorphism), JavaScript (ES6+).
- **Database**: SQLite (Local-first persistence).
- **AI**: Groq API (LLaMA 3.1 8B).

---

## 🚀 Setup & Installation

### 1. Configure Environment
Create a `.env` file in the `backend/` directory:
```env
GROQ_API_KEY=your_key_here
SECRET_KEY=your_secret_key
ALGORITHM=HS256
```

### 2. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Run the Backend
```bash
uvicorn app.main:app --reload
```

### 4. Serve the Frontend
```bash
# From the root directory
python -m http.server 3000
```
Visit **http://localhost:3000/edited.html**

---

## 🧪 Seeding Data
To populate the database with diverse Indian names and preferences:
```bash
cd backend
python seed_db.py
```

<<<<<<< HEAD
---

## 📄 License
Academic Capstone Project — 2026.
Developed by **Anand** with focus on Women's Safety & AI Innovation.
=======
This spins up:
- **FastAPI** on http://localhost:8000
- **PostgreSQL** on localhost:5432
- **Redis** on localhost:6379

---

## 🌐 Vercel Deployment

The project is configured for **Vercel** serverless deployment:
- Backend runs as a Python serverless function (`@vercel/python`)
- Frontend served as static HTML (`@vercel/static`)
- SQLite database stored in `/tmp/` (ephemeral per cold start)

---

## 👥 Team

| Name | Role |
|------|------|
| Anand | Fun-Stack Developer |

---

>>>>>>> e725b08d7b7d46987761c96f60c81e1e0fcccc05
