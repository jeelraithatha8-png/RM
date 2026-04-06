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
from fastapi.encoders import jsonable_encoder
import json
import os
import joblib
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from pydantic import BaseModel

from app.database import get_db, get_redis
from app.models.user import User, Preference
from app.models.interaction import Swipe
from app.schemas.match import MatchListResponse, SwipeActionRequest
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

    # Fetch users already swiped on by current_user
    swiped_result = await db.execute(select(Swipe.target_id).filter(Swipe.user_id == current_user.id))
    swiped_ids = [row[0] for row in swiped_result.all()]

    # Fetch candidates (exclude self and already swiped)
    stmt = select(User).options(selectinload(User.preference)).filter(User.id != current_user.id)
    if swiped_ids:
        stmt = stmt.filter(User.id.not_in(swiped_ids))
    
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
            
        score, explanation = calculate_compatibility(current_user, cand)
        
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
        try:
            matches_data = json.loads(cached)
            return {"matches": matches_data}
        except json.JSONDecodeError:
            pass
        
    matches = await fetch_and_calculate_matches(current_user, db, limit=5)
    
    # Cache the serialized results for 5 minutes (300 seconds)
    encoded_matches = jsonable_encoder(matches)
    await redis.setex(cache_key, 300, json.dumps(encoded_matches))
    
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

@router.post("/swipe")
async def record_swipe(
    swipe_data: SwipeActionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Record a user swipe (LIKE or PASS) and return whether it's a mutual match."""
    from fastapi import HTTPException
    
    # Check if target exists
    target_result = await db.execute(select(User).filter(User.id == swipe_data.target_id))
    if not target_result.scalars().first():
        raise HTTPException(status_code=404, detail="Target user not found")

    new_swipe = Swipe(
        user_id=current_user.id,
        target_id=swipe_data.target_id,
        action=swipe_data.action
    )
    db.add(new_swipe)
    
    mutual_match = False
    if swipe_data.action == "LIKE":
        # Check if the target also liked the current user
        reciprocal = await db.execute(select(Swipe).filter(
            Swipe.user_id == swipe_data.target_id,
            Swipe.target_id == current_user.id,
            Swipe.action == "LIKE"
        ))
        if reciprocal.scalars().first():
            mutual_match = True
            
    await db.commit()
    return {"status": "success", "mutual_match": mutual_match}


@router.post("/swipe/undo")
async def undo_swipe(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove the most recent swipe record for the current user."""
    from sqlalchemy import desc
    result = await db.execute(
        select(Swipe).filter(Swipe.user_id == current_user.id)
        .order_by(desc(Swipe.created_at)).limit(1)
    )
    last_swipe = result.scalars().first()
    
    if not last_swipe:
        return {"status": "ignored", "message": "No swipes to undo"}
        
    target_id = last_swipe.target_id
    await db.delete(last_swipe)
    await db.commit()
    
    return {"status": "success", "undone_target_id": target_id}

# --- ML Match Route --- #
# Load ML Models globally
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "ml_models")
try:
    preprocessor = joblib.load(os.path.join(MODEL_DIR, "preprocessor.pkl"))
    feature_vectors = joblib.load(os.path.join(MODEL_DIR, "feature_vectors.pkl"))
    dataset = joblib.load(os.path.join(MODEL_DIR, "dataset.pkl"))
except Exception as e:
    print(f"Warning: Failed to load ML models: {e}")
    preprocessor, feature_vectors, dataset = None, None, None

class MLMatchRequest(BaseModel):
    occupation: str = "Student"
    sleepPreference: str = "Morning"
    sleepSensitivity: str = "Normal Sleeper"
    livingHabits: str = "Moderate"
    noiseTolerance: str = "Moderate"
    socialEnergy: int = 3
    personality: str = "Ambivert"
    room_type_preference: str = "Shared Room"
    pets: str = "No Pets"
    smoking_drinking: str = "Non-Smoker/Non-Drinker"
    dietary_restrictions: str = "No Restrictions"

@router.post("/ml-match")
async def ml_match(request: MLMatchRequest):
    """Fallback ML endpoint that uses pure scikit-learn models matching CSV dataset strings."""
    if preprocessor is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="ML models not loaded")
    
    try:
        user_profile = {
            'profession': request.occupation,
            'work_shift': request.sleepPreference,
            'sleep_type': request.sleepSensitivity,
            'cleanliness': request.livingHabits,
            'noise_preference': request.noiseTolerance,
            'social_energy_rating': request.socialEnergy,
            
            'personality': request.personality,
            'room_type_preference': request.room_type_preference,
            'pets': request.pets,
            'smoking_drinking': request.smoking_drinking,
            'dietary_restrictions': request.dietary_restrictions
        }
        
        user_df = pd.DataFrame([user_profile])
        user_vector = preprocessor.transform(user_df)
        scores = cosine_similarity(user_vector, feature_vectors).flatten()
        
        best_indices = scores.argsort()[-5:][::-1]
        matches = []
        for idx in best_indices:
            match_row = dataset.iloc[idx]
            match_score = float(scores[idx] * 100)
            
            matches.append({
                "id": str(idx),
                "name": match_row.get('user_name', 'Anonymous User'),
                "profession": match_row.get('profession', 'Unknown'),
                "match_score": round(match_score, 1),
                "work_shift": match_row.get('work_shift', ''),
                "cleanliness": match_row.get('cleanliness', ''),
            })
            
        return {"matches": matches}
    except ValueError as ve:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=str(ve))
