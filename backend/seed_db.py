"""
Database seeder for Nest & Found.
Creates mock users with preferences for local development and testing.
Includes duplicate-email protection to safely re-run.
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import engine, AsyncSessionLocal
from app.models.user import User, Preference
from app.models.chat import Message
from app.utils.security import get_password_hash
from app.models.base import Base

mock_users = [
    { "name": "Sophia", "age": 24, "occupation": "Nurse", "sleep_pref": "Night", "sleep_sense": "Light Sleeper", "personality": "Extrovert", "living_habit": "Organized", "noise_tolerance": "Quiet", "guest_policy": "No Guests" },
    { "name": "Maya", "age": 27, "occupation": "Developer", "sleep_pref": "Morning", "sleep_sense": "Heavy Sleeper", "personality": "Introvert", "living_habit": "Flexible", "noise_tolerance": "Quiet", "guest_policy": "Occasional" },
    { "name": "Emma", "age": 29, "occupation": "Engineer", "sleep_pref": "Morning", "sleep_sense": "Light Sleeper", "personality": "Introvert", "living_habit": "Organized", "noise_tolerance": "Quiet", "guest_policy": "No Guests" },
]

async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with AsyncSessionLocal() as db:
        for idx, u in enumerate(mock_users):
            email = f"user{idx}@example.com"
            
            # Check if user already exists to prevent IntegrityError on re-runs
            existing = await db.execute(select(User).filter(User.email == email))
            if existing.scalars().first() is not None:
                print(f"⏭️  Skipping {email} — already exists.")
                continue
            
            new_u = User(email=email, password_hash=get_password_hash("pass123"), name=u["name"], age=u["age"], occupation=u["occupation"], verification_status=True)
            db.add(new_u)
            await db.commit()
            await db.refresh(new_u)
            
            p = Preference(user_id=new_u.id, sleep_pref=u["sleep_pref"], sleep_sense=u["sleep_sense"], personality=u["personality"], living_habit=u["living_habit"], noise_tolerance=u["noise_tolerance"], guest_policy=u["guest_policy"])
            db.add(p)
            await db.commit()
            print(f"✅ Created {email} ({u['name']})")
    print("\n🎉 Database seeding complete.")

asyncio.run(seed())
