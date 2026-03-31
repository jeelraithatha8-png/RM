from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import settings

# Database setup
engine = create_async_engine(
    settings.DATABASE_URL, 
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# Redis setup
class MockRedis:
    def __init__(self):
        self.cache = {}
    async def setex(self, name, time, value):
        self.cache[name] = value
    async def get(self, name):
        return self.cache.get(name)
    async def close(self):
        pass

# Global instance
_mock_redis = MockRedis()

async def get_redis():
    try:
        yield _mock_redis
    finally:
        pass
