"""
Seeding utility for Roommate Matching System.
Ensures demo users and matching data exist on startup.
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.user import User, Preference
from app.utils.security import get_password_hash

async def seed_data(db: AsyncSession):
    """
    Check for existance of demo user and seed if missing.
    """
    # 1. Check if demo user exists
    result = await db.execute(select(User).filter(User.email == "user0@example.com"))
    demo_user = result.scalars().first()

    if not demo_user:
        print("🌱 Seeding demo data...")
        
        # Create Main Demo User
        main_user = User(
            name="Jyotasana",
            email="user0@example.com",
            password_hash=get_password_hash("pass123"),
            age=24,
            occupation="Nurse",
            verification_status=True
        )
        db.add(main_user)
        await db.commit()
        await db.refresh(main_user)
        
        # Create Main User Preferences
        main_pref = Preference(
            user_id=main_user.id,
            sleep_pref="Night",
            sleep_sense="Light Sleeper",
            personality="Extrovert",
            living_habit="Organized",
            noise_tolerance="Quiet",
            guest_policy="No Guests",
            food_pref="Vegetarian",
            pet_friendly="Pet-Lover",
            smoking_habit="Non-Smoker",
            ac_usage="Night Only"
        )
        db.add(main_pref)

        # 2. Seed other demo users for matching
        other_users = [
            { "name": "Arpita", "email": "user1@example.com", "age": 27, "occupation": "Developer", "prefs": {"sleep_pref": "Morning", "sleep_sense": "Heavy Sleeper", "personality": "Introvert", "living_habit": "Flexible", "noise_tolerance": "Quiet", "guest_policy": "Occasional", "food_pref": "Non-Veg", "pet_friendly": "No Pets", "smoking_habit": "Non-Smoker", "ac_usage": "Always On"} },
            { "name": "Yaashi", "email": "user2@example.com", "age": 22, "occupation": "Student", "prefs": {"sleep_pref": "Night", "sleep_sense": "Heavy Sleeper", "personality": "Extrovert", "living_habit": "Mixed", "noise_tolerance": "Noisy", "guest_policy": "Male Allowed", "food_pref": "Non-Veg", "pet_friendly": "Pet-Lover", "smoking_habit": "Smoker", "ac_usage": "Night Only"} },
            { "name": "Bhoomika", "email": "user3@example.com", "age": 25, "occupation": "Designer", "prefs": {"sleep_pref": "Evening", "sleep_sense": "Light Sleeper", "personality": "Introvert", "living_habit": "Flexible", "noise_tolerance": "Quiet", "guest_policy": "Occasional", "food_pref": "Vegetarian", "pet_friendly": "Pet-Lover", "smoking_habit": "Non-Smoker", "ac_usage": "Eco-friendly"} },
            { "name": "Jeel", "email": "user4@example.com", "age": 26, "occupation": "Chef", "prefs": {"sleep_pref": "Morning", "sleep_sense": "Heavy Sleeper", "personality": "Extrovert", "living_habit": "Organized", "noise_tolerance": "Noisy", "guest_policy": "Occasional", "food_pref": "Non-Veg", "pet_friendly": "No Pets", "smoking_habit": "Occasional", "ac_usage": "Always On"} },
            { "name": "Aditi", "email": "user5@example.com", "age": 23, "occupation": "Content Creator", "prefs": {"sleep_pref": "Night", "sleep_sense": "Light Sleeper", "personality": "Extrovert", "living_habit": "Flexible", "noise_tolerance": "Noisy", "guest_policy": "Male Allowed", "food_pref": "Non-Veg", "pet_friendly": "Pet-Lover", "smoking_habit": "Smoker", "ac_usage": "Night Only"} },
            { "name": "Sneha", "email": "user6@example.com", "age": 28, "occupation": "Lawyer", "prefs": {"sleep_pref": "Morning", "sleep_sense": "Light Sleeper", "personality": "Introvert", "living_habit": "Organized", "noise_tolerance": "Quiet", "guest_policy": "No Guests", "food_pref": "Vegetarian", "pet_friendly": "No Pets", "smoking_habit": "Non-Smoker", "ac_usage": "Eco-friendly"} },
            { "name": "Kavya", "email": "user7@example.com", "age": 24, "occupation": "Engineer", "prefs": {"sleep_pref": "Evening", "sleep_sense": "Heavy Sleeper", "personality": "Ambivert", "living_habit": "Mixed", "noise_tolerance": "Quiet", "guest_policy": "Male Allowed", "food_pref": "Non-Veg", "pet_friendly": "Pet-Lover", "smoking_habit": "Occasional", "ac_usage": "Always On"} },
            { "name": "Pallavi", "email": "user8@example.com", "age": 26, "occupation": "Marketing", "prefs": {"sleep_pref": "Morning", "sleep_sense": "Light Sleeper", "personality": "Extrovert", "living_habit": "Organized", "noise_tolerance": "Noisy", "guest_policy": "Occasional", "food_pref": "Vegetarian", "pet_friendly": "No Pets", "smoking_habit": "Non-Smoker", "ac_usage": "Eco-friendly"} },
        ]

        for u_data in other_users:
            u = User(
                name=u_data["name"],
                email=u_data["email"],
                password_hash=get_password_hash("pass123"),
                age=u_data["age"],
                occupation=u_data["occupation"],
                verification_status=True
            )
            db.add(u)
            await db.commit()
            await db.refresh(u)
            
            p = Preference(user_id=u.id, **u_data["prefs"])
            db.add(p)
        
        await db.commit()
        print("✅ Demo data seeded successfully.")
    else:
        print("✨ Demo data already exists. Skipping seed.")
