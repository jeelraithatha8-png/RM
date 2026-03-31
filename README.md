# 🏠 Nest & Found — Women-Only Roommate Matching System

> **A smart, AI-powered platform for women to find safe, compatible roommates using hybrid Rule-Based + Machine Learning matching.**

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red?logo=python)](https://sqlalchemy.org)
[![Vercel](https://img.shields.io/badge/Deployed-Vercel-black?logo=vercel)](https://vercel.com)

---

## 📌 About

**Nest & Found** is a full-stack web application designed exclusively for women seeking compatible roommates. It uses a **hybrid recommendation engine** combining weighted Rule-Based scoring (sleep preference, guest policy, noise tolerance) with **scikit-learn Cosine Similarity** to produce intelligent compatibility scores on a 1–10 scale.

### Key Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI-Powered Matching** | Hybrid Rule-Based + ML cosine similarity engine (includes age proximity matching) scores compatibility out of 10 |
| 🔐 **Secure Authentication** | JWT-based auth with bcrypt password hashing |
| 🛡️ **Safety Center** | Identity verification, anonymous reporting, emergency alerts |
| 💬 **Real-Time Chat** | Direct messaging between matched users with optimistic DOM rendering |
| 🏘️ **Community Forum** | Discussion threads on safe neighborhoods, rent splitting, etc. |
| 🔍 **Smart Filters** | Filter by verified users, early birds, quiet preference, guest policy |
| 📱 **Responsive UI** | Premium layout with dynamic Light/Dark Mode toggle and glassmorphism styling |

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|-----------|---------|
| **FastAPI** | High-performance async REST API framework |
| **SQLAlchemy 2.0** (Async) | ORM with async session support |
| **SQLite / PostgreSQL** | Database (SQLite for dev, PostgreSQL for production) |
| **Pydantic v2** | Request/response validation and serialization |
| **scikit-learn** | Cosine similarity for ML-based matching |
| **Passlib + bcrypt** | Secure password hashing |
| **python-jose** | JWT token generation and verification |
| **Redis** (optional) | Session caching (falls back to in-memory mock) |

### Frontend
| Technology | Purpose |
|-----------|---------|
| **Vanilla HTML/CSS/JS** | Single-page application |
| **Google Fonts (Inter)** | Premium typography |
| **Font Awesome 6** | Icon library |
| **AOS.js** | Scroll animations |
| **Glassmorphism CSS** | Modern frosted-glass UI aesthetic |

---

## 📁 Project Structure

```
Roommate-Matching-System/
├── index2.html                    # Frontend SPA
├── vercel.json                    # Vercel deployment config
├── requirements.txt               # Python dependencies (root)
├── .gitignore
│
├── backend/
│   ├── requirements.txt           # Python dependencies
│   ├── Dockerfile                 # Docker build config
│   ├── docker-compose.yml         # Multi-service orchestration
│   ├── seed_db.py                 # Database seeder script
│   │
│   └── app/
│       ├── main.py                # FastAPI application entry point
│       ├── config.py              # Environment & settings management
│       ├── database.py            # Async engine, session, Redis mock
│       │
│       ├── models/
│       │   ├── base.py            # SQLAlchemy DeclarativeBase
│       │   ├── user.py            # User & Preference models
│       │   └── chat.py            # Message & Report models
│       │
│       ├── routes/
│       │   ├── auth.py            # Register, Login endpoints
│       │   ├── users.py           # Profile CRUD
│       │   ├── matches.py         # Matching & filtering endpoints
│       │   ├── chat.py            # Send/receive messages
│       │   └── safety.py          # Report, verify, emergency alert
│       │
│       ├── schemas/
│       │   ├── auth.py            # Token schemas
│       │   ├── user.py            # User/Preference request/response
│       │   ├── chat.py            # Message schemas
│       │   └── match.py           # Match result schemas
│       │
│       ├── recommender/
│       │   ├── engine.py          # Hybrid Rule+ML scoring engine
│       │   └── loader.py          # Kaggle dataset ingestion
│       │
│       └── utils/
│           └── security.py        # JWT, bcrypt, OAuth2 utilities
```

---

## 🚀 Setup Instructions

### Prerequisites
- **Python 3.11+**
- **pip** package manager
- **Git**

### 1. Clone the Repository
```bash
git clone https://github.com/Anand2k29/Roommate-Matching-System-----YOLO.git
cd Roommate-Matching-System-----YOLO
```

### 2. Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Run the Backend Server
```bash
uvicorn app.main:app --reload --port 8000
```
The API will be live at **http://localhost:8000**

### 4. Serve the Frontend
Open a new terminal at the project root:
```bash
python -m http.server 3000
```
Visit **http://localhost:3000/index2.html** in your browser.

### 5. API Documentation (auto-generated)
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔌 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/register` | Register a new user |
| `POST` | `/api/v1/auth/login` | Login (returns JWT token) |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/users/me` | Get current user profile |
| `PUT` | `/api/v1/users/update` | Update profile & preferences |

### Matches
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/matches` | Get all compatible matches |
| `GET` | `/api/v1/matches/top` | Get top 5 matches |
| `GET` | `/api/v1/matches/filter?type=X` | Filter matches (verified, quiet, earlyBird, noMaleGuests) |

### Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/chat/send` | Send a message |
| `GET` | `/api/v1/chat/{user_id}` | Get chat history with a user |

### Safety
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/safety/report-user` | Report a user |
| `POST` | `/api/v1/safety/verify-id` | Verify government ID |
| `POST` | `/api/v1/safety/emergency-alert` | Trigger emergency alert |

---

## 🧠 Recommendation Engine

The matching system uses a **hybrid approach**:

1. **Rule-Based Scoring** (50% weight)
   - High priority (5 pts each): Sleep schedule, Guest policy, Noise tolerance
   - Medium priority (3 pts each): Personality type, Living habits
   - Low priority (1 pt): Sleep sensitivity

2. **ML Cosine Similarity** (50% weight)
   - One-hot encodes user preferences into feature vectors
   - Computes cosine similarity between user pairs
   - Normalizes to 0–1 scale

3. **Final Score** = `(rule_score × 0.5 + ml_score × 0.5) × 10`

---

## 🐳 Docker Deployment (Alternative)

```bash
cd backend
docker-compose up --build
```

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
| Anand | Full-Stack Developer |

---

## 📄 License

This project is developed as an academic capstone project.