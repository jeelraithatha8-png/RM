import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, Preference
from app.utils.security import get_password_hash

async def load_kaggle_dataset(file_path: str, db: AsyncSession):
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error loading CSV {file_path}: {str(e)}")
        return False
        
    # Expected columns roughly mapping user and preference schema
    # df.fillna("Unknown", inplace=True)
    
    for index, row in df.iterrows():
        email = f"user_{index}@nestfound.local"
        
        # Simple check if exists
        # In a robust scenario we'd do a SELECT first
        hashed_pass = get_password_hash("password123")
        
        user = User(
            email=email,
            name=str(row.get("Name", f"User {index}")),
            age=int(row.get("Age", 20)),
            password_hash=hashed_pass,
            occupation=str(row.get("Occupation", "Student")),
            verification_status=True
        )
        db.add(user)
        # We need user.id, so we must commit to get it
        await db.commit()
        await db.refresh(user)
        
        pref = Preference(
            user_id=user.id,
            sleep_pref=str(row.get("Sleep Preference", "Night")),
            sleep_sense=str(row.get("Sleep Sensitivity", "Light")),
            personality=str(row.get("Personality", "Ambivert")),
            living_habit=str(row.get("Living Habit", "Flexible")),
            noise_tolerance=str(row.get("Noise Tolerance", "Moderate")),
            guest_policy=str(row.get("Guest Policy", "Occasional"))
        )
        db.add(pref)
        
    await db.commit()
    return True
