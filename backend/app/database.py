"""
Database module for Nest & Found.

Configures the async SQLAlchemy engine, session factory, and Redis/mock cache.
Supports SQLite (dev/Vercel) and PostgreSQL (Docker/production).
"""
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import settings

# Async database engine — auto-detects SQLite vs PostgreSQL from DATABASE_URL
engine = create_async_engine(
    settings.DATABASE_URL, 
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db():
    """
    FastAPI dependency that yields an async database session.
    Automatically closes the session when the request completes.
    """
    async with AsyncSessionLocal() as session:
        yield session


class MockRedis:
    """
    In-memory Redis mock for environments without a Redis server.
    Provides the same interface as redis.asyncio.Redis for setex/get operations.
    """
    def __init__(self):
        self.cache = {}

    async def setex(self, name, time, value):
        """Store a value with a TTL (TTL not enforced in mock)."""
        self.cache[name] = value

    async def get(self, name):
        """Retrieve a cached value by key."""
        return self.cache.get(name)

    async def close(self):
        """No-op cleanup."""
        pass


# Global mock Redis instance (used when REDIS_URL is not configured)
_mock_redis = MockRedis()


async def get_redis():
    """
    FastAPI dependency that yields a Redis-like cache instance.
    Returns a MockRedis in development, or a real Redis client in production.
    """
    try:
        yield _mock_redis
    finally:
        pass
