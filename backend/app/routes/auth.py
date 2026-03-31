"""
Authentication routes: Register and Login.
Handles user creation with bcrypt hashing and JWT token issuance.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from datetime import timedelta

from app.database import get_db, get_redis
from app.models.user import User, Preference
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import Token
from app.utils.security import verify_password, get_password_hash, create_access_token
from app.config import settings

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user account.
    
    - Validates password length (minimum 6 characters)
    - Checks for duplicate email
    - Creates user with hashed password
    - Optionally creates preference record
    """
    # Validate password strength
    if len(user_in.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long"
        )

    # Check if user already exists
    result = await db.execute(select(User).filter(User.email == user_in.email))
    if result.scalars().first() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered. Please use a different email or sign in."
        )
        
    hashed_pass = get_password_hash(user_in.password)
    new_user = User(
        email=user_in.email,
        name=user_in.name,
        password_hash=hashed_pass,
        age=user_in.age,
        occupation=user_in.occupation
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Create preferences if provided
    if user_in.preferences:
        pref = Preference(user_id=new_user.id, **user_in.preferences.model_dump(exclude_unset=True))
        db.add(pref)
        await db.commit()
        
    # Reload with preference relationship
    res = await db.execute(
        select(User).options(selectinload(User.preference)).filter(User.id == new_user.id)
    )
    return res.scalars().first()


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis)
):
    """
    Authenticate user and return a JWT access token.
    
    Accepts OAuth2 form data (username = email, password).
    """
    result = await db.execute(select(User).filter(User.email == form_data.username))
    user = result.scalars().first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    # Cache session in redis (or mock)
    await redis.setex(f"session:{user.id}", settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60, access_token)
    
    return {"access_token": access_token, "token_type": "bearer"}
