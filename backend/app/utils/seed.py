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
            {
                "name": "Arpita", "email": "arpita@example.com", "age": 27, "occupation": "Developer",
                "prefs": {"sleep_pref": "Morning", "personality": "Introvert", "living_habit": "Flexible", "food_pref": "Non-Veg"}
            },
            {
                "name": "Yaashi", "email": "yaashi@example.com", "age": 22, "occupation": "Student",
                "prefs": {"sleep_pref": "Night", "personality": "Extrovert", "living_habit": "Mixed", "food_pref": "Vegetarian"}
            },
            {
                "name": "Bhoomika", "email": "bhoomika@example.com", "age": 25, "occupation": "Designer",
                "prefs": {"sleep_pref": "Evening", "personality": "Introvert", "living_habit": "Flexible", "food_pref": "Vegetarian"}
            }
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
