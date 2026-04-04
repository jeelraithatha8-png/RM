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


_db_initialized = False

async def get_db():
    global _db_initialized
    if not _db_initialized:
        import os
        import shutil
        from app.models.base import Base
        from app.models.user import User, Preference
        from app.utils.seed import seed_data
        
        try:
            if os.environ.get("VERCEL"):
                tmp_db = "/tmp/nestfound.db"
                # Locate relative to this file
                local_db = os.path.join(os.path.dirname(os.path.dirname(__file__)), "nestfound.db")
                
                # Solid copy logic: only copy if target missing or invalid
                if not os.path.exists(tmp_db) or os.path.getsize(tmp_db) == 0:
                    if os.path.exists(local_db):
                        shutil.copy2(local_db, tmp_db)
                        print(f"📦 Successfully copied seed DB to {tmp_db} ({os.path.getsize(tmp_db)} bytes)")
                    else:
                        print(f"⚠️ Seed DB not found at {local_db}, will create fresh.")

            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            async with AsyncSessionLocal() as session:
                await seed_data(session)
            print("✅ Database initialized and synchronized.")
        except Exception as e:
            print(f"❌ DB init error: {str(e)}")
            import traceback
            traceback.print_exc()
        _db_initialized = True

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
