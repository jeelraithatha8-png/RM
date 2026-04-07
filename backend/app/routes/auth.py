from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
from app.database import get_db
from app.models import User
from app.schemas import Token, UserLogin, UserResponse
from app.auth import verify_password, create_access_token, get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/login", response_model=Token)
async def login(user_cred: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login endpoint for users"""
    logger.info(f"Login attempt for email: {user_cred.email}")
    
    # Find user by email
    result = await db.execute(select(User).where(User.email == user_cred.email))
    user = result.scalar_one_or_none()
    
    if not user:
        logger.warning(f"User not found: {user_cred.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(user_cred.password, user.hashed_password):
        logger.warning(f"Invalid password for: {user_cred.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id}
    )
    
    logger.info(f"Login successful for: {user_cred.email}")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name
        }
    }

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    logger.info(f"Registration attempt for: {user_data.email}")
    
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name if hasattr(user_data, 'full_name') else user_data.email.split('@')[0]
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    logger.info(f"User registered successfully: {user_data.email}")
    return new_user

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user
