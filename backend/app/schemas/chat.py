from pydantic import BaseModel
from datetime import datetime
from typing import List

class MessageCreate(BaseModel):
    receiver_id: int
    content: str

class MessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
