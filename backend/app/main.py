"""
Nest & Found Backend — FastAPI Application Entry Point.

A women-only roommate matching system with hybrid AI recommendation engine.
This module initializes the FastAPI app, configures CORS, registers
all route modules, and manages the database lifecycle.
"""
import sys
import os

# Ensure 'backend/' is on sys.path for Vercel serverless deployment
_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine
from app.models.base import Base

# Routers
from app.routes.auth import router as auth_router
from app.routes.users import router as user_router
from app.routes.matches import router as match_router
from app.routes.chat import router as chat_router
from app.routes.safety import router as safety_router

from app.utils.seed import seed_data
from app.database import AsyncSessionLocal


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle manager.
    Creates database tables on startup, seeds demo data, and disposes the engine on shutdown.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Run seeding logic
    async with AsyncSessionLocal() as session:
        await seed_data(session)
        
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description=(
        "Backend API for **Roommate Matching System**: A Women-Only Personalized Living Platform.\n\n"
        "Features:\n"
        "- 🤖 Hybrid Rule-Based + ML (Cosine Similarity) matching engine\n"
        "- 🔐 JWT authentication with bcrypt password hashing\n"
        "- 🛡️ Safety reporting and identity verification\n"
        "- 💬 Real-time messaging between matched users\n"
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

from fastapi.responses import JSONResponse
from fastapi import Request
import traceback

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error", "detail": str(exc), "traceback": traceback.format_exc()}
    )

# CORS — allow all origins for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules
app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["Auth"])
app.include_router(user_router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])
app.include_router(match_router, prefix=f"{settings.API_V1_STR}/matches", tags=["Matches"])
app.include_router(chat_router, prefix=f"{settings.API_V1_STR}/chat", tags=["Chat"])
app.include_router(safety_router, prefix=f"{settings.API_V1_STR}/safety", tags=["Safety"])


@app.get("/", tags=["Health"])
def read_root():
    """Root endpoint — API health check."""
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint for monitoring and deployment verification."""
    return {"status": "ok"}
