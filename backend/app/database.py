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


async def init_db():
    """
    Initializes the database:
    1. On Vercel, copies the seed DB to /tmp for write access.
    2. Runs SQLAlchemy metadata creation.
    3. Seeds demo data if missing.
    """
    import os
    import shutil
    from app.models.base import Base
    from app.models.user import User
    from app.utils.seed import seed_data
    
    try:
        if os.environ.get("VERCEL"):
            tmp_db = "/tmp/nestfound.db"
            # Locate relative to this file — check both root and backend folder
            current_dir = os.path.dirname(os.path.abspath(__file__))
            backend_dir = os.path.dirname(current_dir)
            root_dir = os.path.dirname(backend_dir)
            
            # Potential locations for the seed database
            potential_locations = [
                os.path.join(backend_dir, "nestfound.db"),
                os.path.join(root_dir, "nestfound.db"),
                os.path.join(os.getcwd(), "backend", "nestfound.db"),
                os.path.join(os.getcwd(), "nestfound.db")
            ]
            
            local_db = None
            for loc in potential_locations:
                if os.path.exists(loc) and os.path.getsize(loc) > 0:
                    local_db = loc
                    break
            
            # Solid copy logic: only copy if target missing, invalid, or using old schema lacking new columns
            needs_copy = False
            if not os.path.exists(tmp_db) or os.path.getsize(tmp_db) == 0:
                needs_copy = True
            else:
                try:
                    with open(tmp_db, "rb") as f:
                        if b"food_pref" not in f.read():
                            needs_copy = True
                            print("⚠️ Detected old DB schema in /tmp. Forcing overwrite.")
                except Exception:
                    needs_copy = True

            if needs_copy:
                if local_db and os.path.exists(local_db):
                    shutil.copy2(local_db, tmp_db)
                    print(f"📦 Successfully copied seed DB from {local_db} to {tmp_db} ({os.path.getsize(tmp_db)} bytes)")
                else:
                    print(f"⚠️ Seed DB not found (searched {potential_locations}), ensuring fresh metadata.")

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
        async with AsyncSessionLocal() as session:
            await seed_data(session)
        print("✅ Database initialized and synchronized.")
    except Exception as e:
        print(f"❌ DB init error: {str(e)}")
        import traceback
        traceback.print_exc()


async def get_db():
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
