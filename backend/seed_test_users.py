import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models import User
from app.auth import get_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

async def seed_users():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Test user with credentials from screenshot
        test_user = User(
            email="user0@example.com",
            hashed_password=get_password_hash("password123"),  # Use a simple password
            full_name="Test User",
            is_active=True
        )
        
        # Add more test users for matching
        users = [
            test_user,
            User(
                email="alice@example.com",
                hashed_password=get_password_hash("password123"),
                full_name="Alice Sharma",
                is_active=True
            ),
            User(
                email="bobita@example.com",
                hashed_password=get_password_hash("password123"),
                full_name="Bobita Patel",
                is_active=True
            ),
        ]
        
        for user in users:
            existing = await session.execute(
                select(User).where(User.email == user.email)
            )
            if not existing.scalar_one_or_none():
                session.add(user)
        
        await session.commit()
        print("✅ Test users seeded successfully!")
        print("📧 Email: user0@example.com")
        print("🔑 Password: password123")

if __name__ == "__main__":
    asyncio.run(seed_users())
