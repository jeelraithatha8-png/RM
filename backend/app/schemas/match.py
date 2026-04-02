from pydantic import BaseModel
from typing import List, Optional
from app.schemas.user import UserResponse

class MatchResult(BaseModel):
    user: UserResponse
    compatibility_score: float  # Scale 0 to 10
    explanation: Optional[str] = None

class MatchListResponse(BaseModel):
    matches: List[MatchResult]

class SwipeActionRequest(BaseModel):
    target_id: int
    action: str  # "LIKE" or "PASS"

