from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import Optional, List
from redis.asyncio import Redis
import json

from app.database import get_db, get_redis
from app.models.user import User, Preference
from app.schemas.match import MatchListResponse
from app.utils.security import get_current_user
from app.recommender.engine import calculate_compatibility

router = APIRouter()

async def fetch_and_calculate_matches(current_user: User, db: AsyncSession, limit: int = 20, filter_type: Optional[str] = None):
    # Fetch current user's preferences
    result = await db.execute(select(Preference).filter(Preference.user_id == current_user.id))
    current_pref = result.scalars().first()
    
    if not current_pref:
        return []

    # Fetch candidates (others)
    stmt = select(User).options(selectinload(User.preference)).filter(User.id != current_user.id)
    
    # Apply dynamic filtering
    if filter_type == "verified":
        stmt = stmt.filter(User.verification_status == True)
        
    cand_result = await db.execute(stmt)
    candidates = cand_result.scalars().all()
    
    matches = []
    for cand in candidates:
        if cand.preference:
            # Further dynamic filtering on preferences (e.g. quiet, earlyBird) can be evaluated here or in SQL
            if filter_type == "quiet" and cand.preference.noise_tolerance != "Quiet":
                continue
            if filter_type == "earlyBird" and cand.preference.sleep_pref != "Morning":
                continue
                
            score, explanation = calculate_compatibility(current_pref, cand.preference)
            # Only include reasonable matches > 4.0
            if score > 4.0:
                matches.append({
                    "user": cand,
                    "compatibility_score": score,
                    "explanation": explanation
                })
                
    # Sort by score descending
    matches = sorted(matches, key=lambda x: x["compatibility_score"], reverse=True)
    return matches[:limit]


@router.get("", response_model=MatchListResponse)
async def get_matches(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    matches = await fetch_and_calculate_matches(current_user, db)
    return {"matches": matches}

@router.get("/top", response_model=MatchListResponse)
async def get_top_matches(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)):
    # Example of Redis caching
    cache_key = f"top_matches_{current_user.id}"
    cached = await redis.get(cache_key)
    
    if cached:
        # In a real app we'd serialize this properly to pydantic models or dicts
        # For simplicity here, we simulate cache hit (this returns raw json string if implemented fully)
        # return json.loads(cached)
        pass 
        
    matches = await fetch_and_calculate_matches(current_user, db, limit=5)
    
    # Store minimal response in cache (only user IDs and score)
    # await redis.setex(cache_key, 3600, json_encoded_matches) 
    
    return {"matches": matches}

@router.get("/filter", response_model=MatchListResponse)
async def get_filtered_matches(
    type: str = Query(..., description="verified|quiet|earlyBird"),
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    matches = await fetch_and_calculate_matches(current_user, db, limit=20, filter_type=type)
    return {"matches": matches}
