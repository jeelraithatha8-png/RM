import asyncio
import os
import sys

# Add backend to sys.path
sys.path.append(os.path.abspath('e:/LAmbi/Roommate-Matching-System/backend'))

from app.database import engine, AsyncSessionLocal
from app.models.base import Base
from app.models.user import User
from app.utils.seed import seed_data
from sqlalchemy.future import select

async def verify():
    print("🚀 Starting verification...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        await seed_data(session)
        
        # Verify users exist
        result = await session.execute(select(User))
        users = result.scalars().all()
        print(f"👥 Found {len(users)} users in database.")
        for u in users:
            print(f"  - {u.name} ({u.email})")
            
        if any(u.email == "user0@example.com" for u in users):
            print("✅ Demo user found!")
        else:
            print("❌ Demo user NOT found!")

if __name__ == "__main__":
    asyncio.run(verify())
