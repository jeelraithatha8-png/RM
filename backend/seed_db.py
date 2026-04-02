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
    { "name": "Jyotasana", "age": 24, "occupation": "Nurse", "sleep_pref": "Night", "sleep_sense": "Light Sleeper", "personality": "Extrovert", "living_habit": "Organized", "noise_tolerance": "Quiet", "guest_policy": "No Guests", "food_pref": "Vegetarian", "pet_friendly": "Pet-Lover", "smoking_habit": "Non-Smoker", "ac_usage": "Eco-friendly" },
    { "name": "Arpita", "age": 27, "occupation": "Developer", "sleep_pref": "Morning", "sleep_sense": "Heavy Sleeper", "personality": "Introvert", "living_habit": "Flexible", "noise_tolerance": "Quiet", "guest_policy": "Occasional", "food_pref": "Non-Veg", "pet_friendly": "No Pets", "smoking_habit": "Non-Smoker", "ac_usage": "Always On" },
    { "name": "Yaashi", "age": 22, "occupation": "Student", "sleep_pref": "Night", "sleep_sense": "Heavy Sleeper", "personality": "Extrovert", "living_habit": "Mixed", "noise_tolerance": "Noisy", "guest_policy": "Male Allowed", "food_pref": "Non-Veg", "pet_friendly": "Pet-Lover", "smoking_habit": "Smoker", "ac_usage": "Night Only" },
    { "name": "Bhoomika", "age": 25, "occupation": "Designer", "sleep_pref": "Evening", "sleep_sense": "Light Sleeper", "personality": "Introvert", "living_habit": "Flexible", "noise_tolerance": "Quiet", "guest_policy": "Occasional", "food_pref": "Vegetarian", "pet_friendly": "Pet-Lover", "smoking_habit": "Non-Smoker", "ac_usage": "Eco-friendly" },
    { "name": "Jeel", "age": 26, "occupation": "Chef", "sleep_pref": "Morning", "sleep_sense": "Heavy Sleeper", "personality": "Extrovert", "living_habit": "Organized", "noise_tolerance": "Noisy", "guest_policy": "Occasional", "food_pref": "Non-Veg", "pet_friendly": "No Pets", "smoking_habit": "Occasional", "ac_usage": "Always On" },
    { "name": "Aditi", "age": 23, "occupation": "Content Creator", "sleep_pref": "Night", "sleep_sense": "Light Sleeper", "personality": "Extrovert", "living_habit": "Flexible", "noise_tolerance": "Noisy", "guest_policy": "Male Allowed", "food_pref": "Non-Veg", "pet_friendly": "Pet-Lover", "smoking_habit": "Smoker", "ac_usage": "Night Only" },
    { "name": "Sneha", "age": 28, "occupation": "Lawyer", "sleep_pref": "Morning", "sleep_sense": "Light Sleeper", "personality": "Introvert", "living_habit": "Organized", "noise_tolerance": "Quiet", "guest_policy": "No Guests", "food_pref": "Vegetarian", "pet_friendly": "No Pets", "smoking_habit": "Non-Smoker", "ac_usage": "Eco-friendly" },
    { "name": "Kavya", "age": 24, "occupation": "Engineer", "sleep_pref": "Evening", "sleep_sense": "Heavy Sleeper", "personality": "Ambivert", "living_habit": "Mixed", "noise_tolerance": "Quiet", "guest_policy": "Male Allowed", "food_pref": "Non-Veg", "pet_friendly": "Pet-Lover", "smoking_habit": "Occasional", "ac_usage": "Always On" },
    { "name": "Pallavi", "age": 26, "occupation": "Marketing", "sleep_pref": "Morning", "sleep_sense": "Light Sleeper", "personality": "Extrovert", "living_habit": "Organized", "noise_tolerance": "Noisy", "guest_policy": "Occasional", "food_pref": "Vegetarian", "pet_friendly": "No Pets", "smoking_habit": "Non-Smoker", "ac_usage": "Eco-friendly" },
]

async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with AsyncSessionLocal() as db:
        for idx, u in enumerate(mock_users):
            email = f"user{idx}@example.com"
            
            # Check if user already exists
            existing = await db.execute(select(User).filter(User.email == email))
            existing_user = existing.scalars().first()
            if existing_user is not None:
                existing_user.name = u["name"]
                await db.commit()
                print(f"🔄 Updated {email} to {u['name']}")
                continue
            
            new_u = User(email=email, password_hash=get_password_hash("pass123"), name=u["name"], age=u["age"], occupation=u["occupation"], verification_status=True)
            db.add(new_u)
            await db.commit()
            await db.refresh(new_u)
            
            p = Preference(
                user_id=new_u.id, 
                sleep_pref=u["sleep_pref"], 
                sleep_sense=u["sleep_sense"], 
                personality=u["personality"], 
                living_habit=u["living_habit"], 
                noise_tolerance=u["noise_tolerance"], 
                guest_policy=u["guest_policy"],
                food_pref=u["food_pref"],
                pet_friendly=u["pet_friendly"],
                smoking_habit=u["smoking_habit"],
                ac_usage=u["ac_usage"]
            )
            db.add(p)
            await db.commit()
            print(f"✅ Created {email} ({u['name']})")
    print("\n🎉 Database seeding complete.")

asyncio.run(seed())
