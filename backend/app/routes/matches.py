"""
Match routes: Smart roommate matching with hybrid Rule+ML scoring.
Supports filtering by verification status, sleep preference,
noise tolerance, and guest policy.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import Optional

from app.database import get_db, get_redis
from app.models.user import User, Preference
from app.schemas.match import MatchListResponse
from app.utils.security import get_current_user
from app.recommender.engine import calculate_compatibility

router = APIRouter()

# Map frontend filter names to backend logic
FILTER_ALIASES = {
    "quietOnly": "quiet",
    "quiet": "quiet",
    "earlyBird": "earlyBird",
    "verified": "verified",
    "noMaleGuests": "noMaleGuests",
}


async def fetch_and_calculate_matches(
    current_user: User,
    db: AsyncSession,
    limit: int = 20,
    filter_type: Optional[str] = None
):
    """
    Core matching logic:
    1. Load current user's preferences
    2. Fetch candidate users with preferences
    3. Apply optional filters
    4. Score each candidate with the hybrid engine
    5. Return sorted matches above threshold
    """
    # Fetch current user's preferences
    result = await db.execute(select(Preference).filter(Preference.user_id == current_user.id))
    current_pref = result.scalars().first()
    
    if not current_pref:
        return []

    # Resolve filter alias
    resolved_filter = FILTER_ALIASES.get(filter_type, filter_type)

    # Fetch candidates (exclude self)
    stmt = select(User).options(selectinload(User.preference)).filter(User.id != current_user.id)
    
    # SQL-level filtering for verified
    if resolved_filter == "verified":
        stmt = stmt.filter(User.verification_status == True)
        
    cand_result = await db.execute(stmt)
    candidates = cand_result.scalars().all()
    
    matches = []
    for cand in candidates:
        if not cand.preference:
            continue
            
        # Apply preference-level filters
        if resolved_filter == "quiet" and cand.preference.noise_tolerance != "Quiet":
            continue
        if resolved_filter == "earlyBird" and cand.preference.sleep_pref != "Morning":
            continue
        if resolved_filter == "noMaleGuests" and cand.preference.guest_policy == "Male Allowed":
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
async def get_matches(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all compatible roommate matches for the current user."""
    matches = await fetch_and_calculate_matches(current_user, db)
    return {"matches": matches}


@router.get("/top", response_model=MatchListResponse)
async def get_top_matches(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis)
):
    """Get top 5 most compatible matches (with optional Redis caching)."""
    cache_key = f"top_matches_{current_user.id}"
    cached = await redis.get(cache_key)
    
    if cached:
        pass  # Cache hit — in production, deserialize and return
        
    matches = await fetch_and_calculate_matches(current_user, db, limit=5)
    return {"matches": matches}


@router.get("/filter", response_model=MatchListResponse)
async def get_filtered_matches(
    type: str = Query(..., description="Filter type: verified | quiet | quietOnly | earlyBird | noMaleGuests"),
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """Get matches filtered by a specific criteria."""
    matches = await fetch_and_calculate_matches(current_user, db, limit=20, filter_type=type)
    return {"matches": matches}
