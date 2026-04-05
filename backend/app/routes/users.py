from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.database import get_db
from app.models.user import User, Preference
from app.schemas.user import UserUpdate, UserResponse
from app.utils.security import get_current_user

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def read_user_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/all", response_model=List[UserResponse])
async def get_all_users(
    search: Optional[str] = Query(None, description="Search by name or occupation"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all registered users with their preferences.
    Supports optional search filtering by name or occupation.
    """
    stmt = select(User).options(selectinload(User.preference))
    
    if search:
        search_term = f"%{search}%"
        stmt = stmt.filter(
            (User.name.ilike(search_term)) | (User.occupation.ilike(search_term))
        )
    
    stmt = stmt.order_by(User.created_at.desc())
    result = await db.execute(stmt)
    users = result.scalars().all()
    return users

@router.put("/update", response_model=UserResponse)
async def update_user_me(user_in: UserUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if user_in.name is not None:
        current_user.name = user_in.name
    if user_in.age is not None:
        current_user.age = user_in.age
    if user_in.occupation is not None:
        current_user.occupation = user_in.occupation

    if user_in.preferences:
        # Check if user has preferences, otherwise create
        result = await db.execute(select(Preference).filter(Preference.user_id == current_user.id))
        pref = result.scalars().first()
        
        pref_data = user_in.preferences.model_dump(exclude_unset=True)
        if pref:
            for key, value in pref_data.items():
                setattr(pref, key, value)
        else:
            new_pref = Preference(user_id=current_user.id, **pref_data)
            db.add(new_pref)

    await db.commit()
    await db.refresh(current_user)
    return current_user
