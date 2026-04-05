# Roommate Matching Backend

This is the Python (FastAPI) backend for **Roommate Matching**, a women-only roommate matching system. It features an advanced recommendation engine merging Rule-Based heuristics with Machine Learning `cosine_similarity`.

## 📦 Tech Stack
- **API Framework**: FastAPI
- **Database**: PostgreSQL (via SQLAlchemy Async)
- **Cache**: Redis
- **ML Engine**: Scikit-Learn, Pandas (for Kaggle ingestion)
- **Ops**: Docker, Docker Compose

## 🚀 Setup Instructions

### 1. Requirements
- Docker and Docker Compose installed.

### 2. Run Locally with Docker
Create an `.env` file (or just use defaults in config.py) inside `backend/`:
```bash
docker-compose up --build
```
This will spin up:
1. `web` on http://localhost:8000
2. `db` on Postgres localhost:5432
3. `redis` on localhost:6379

### 3. API Documentation
Once running, interactive API docs are generated automatically here:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 4. Loading the Kaggle Dataset
By default, the database is empty. To ingest the roommate dataset:
1. Download the dataset from Kaggle.
2. Place it in `backend/data/dataset.csv`.
3. Create a quick helper script to invoke `app.recommender.loader.load_kaggle_dataset`.

### 🧠 Architecture Overview
- **`app/routes/`**: Distinct controllers grouped by domain (`matches`, `auth`, `users`).
- **`app/recommender/engine.py`**: The dynamic matching logic scoring out of 10 using strict weights for non-negotiables (`sleepPref`, `guestPolicy`) and Cosine Similarity mapping for lifestyle elements.
- **`app/utils/security.py`**: Passlib bcrypt hashing and JWT state management injected securely via FastAPI `Depends`.
