from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User
from app.schemas import UserLogin, Token
from app.auth import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/login", response_model=Token)
async def login(user_cred: UserLogin, db: AsyncSession = Depends(get_db)):
    # Debug: Print received credentials
    print(f"Login attempt for email: {user_cred.email}")
    
    # Query user from database
    result = await db.execute(
        select(User).where(User.email == user_cred.email)
    )
    user = result.scalar_one_or_none()
    
    # Debug: Check if user exists
    if not user:
        print(f"❌ User not found: {user_cred.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Debug: Verify password
    if not verify_password(user_cred.password, user.hashed_password):
        print(f"❌ Invalid password for: {user_cred.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id}
    )
    
    print(f"✅ Login successful for: {user_cred.email}")
    return {"access_token": access_token, "token_type": "bearer"}
