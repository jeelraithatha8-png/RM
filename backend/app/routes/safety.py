from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models.user import User
from app.models.chat import Report
from app.utils.security import get_current_user

router = APIRouter()

class ReportCreate(BaseModel):
    reported_user_id: int
    reason: str

@router.post("/report-user", status_code=status.HTTP_201_CREATED)
async def report_user(
    report_in: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Check if reported user exists
    result = await db.execute(select(User).filter(User.id == report_in.reported_user_id))
    reported = result.scalars().first()
    if not reported:
        raise HTTPException(status_code=404, detail="User to report not found")
        
    report = Report(
        reporter_id=current_user.id,
        reported_user_id=reported.id,
        reason=report_in.reason
    )
    db.add(report)
    await db.commit()
    return {"status": "User reported successfully"}

@router.post("/verify-id")
async def verify_id(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # In a real system, this would trigger an async 3rd party KYC flow (e.g. Stripe Identity)
    current_user.verification_status = True
    await db.commit()
    await db.refresh(current_user)
    return {"status": "ID verified successfully. Badge added."}

@router.post("/emergency-alert")
async def trigger_emergency(current_user: User = Depends(get_current_user)):
    # In a broader product, this hits SMS gateways (Twilio), emails emergency contacts, or authorities
    # For now, it's a simulated endpoint
    return {
        "status": "ALERT TRIGGERED",
        "action": f"Emergency contacts for {current_user.name} have been notified.",
        "user_location_requested": True
    }
