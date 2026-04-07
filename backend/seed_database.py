import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models import User, Base
from app.auth import get_password_hash
import os

DATABASE_URL = "sqlite+aiosqlite:///./roommate.db"

async def seed_database():
    """Seed the database with test users"""
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Test users
        users = [
            User(
                email="user0@example.com",
                hashed_password=get_password_hash("password123"),
                full_name="Test User",
                age=22,
                occupation="Student",
                sleep_schedule="9pm-6am",
                noise_tolerance="Medium",
                guest_policy="Friendly",
                cleaning_habit="Organized"
            ),
            User(
                email="alice@example.com",
                hashed_password=get_password_hash("password123"),
                full_name="Alice Sharma",
                age=24,
                occupation="Software Engineer",
                sleep_schedule="11pm-8am",
                noise_tolerance="Low",
                guest_policy="Rarely",
                cleaning_habit="Very Organized"
            ),
            User(
                email="priya@example.com",
                hashed_password=get_password_hash("password123"),
                full_name="Priya Patel",
                age=23,
                occupation="Medical Student",
                sleep_schedule="10pm-7am",
                noise_tolerance="High",
                guest_policy="Occasional",
                cleaning_habit="Moderate"
            )
        ]
        
        for user in users:
            session.add(user)
        
        await session.commit()
        
        print("✅ Database seeded successfully!")
        print("\n📧 Test Credentials:")
        print("1. Email: user0@example.com, Password: password123")
        print("2. Email: alice@example.com, Password: password123")
        print("3. Email: priya@example.com, Password: password123")
        
        # Verify users were created
        result = await session.execute(select(User))
        all_users = result.scalars().all()
        print(f"\n👥 Total users created: {len(all_users)}")

if __name__ == "__main__":
    asyncio.run(seed_database())
