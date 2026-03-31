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

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB (Create tables if they don't exist)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Cleanup logic if any
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Backend API for Nest & Found: A Women-Only Roommate Matching System",
    lifespan=lifespan
)

# CORS setup for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to the frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["Auth"])
app.include_router(user_router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])
app.include_router(match_router, prefix=f"{settings.API_V1_STR}/matches", tags=["Matches"])
app.include_router(chat_router, prefix=f"{settings.API_V1_STR}/chat", tags=["Chat"])
app.include_router(safety_router, prefix=f"{settings.API_V1_STR}/safety", tags=["Safety"])

@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API. Visit /docs for documentation."}
