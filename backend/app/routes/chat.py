"""
Chat routes: Send messages and retrieve conversation history.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.chat import Message
from app.schemas.chat import MessageCreate, MessageResponse
from app.utils.security import get_current_user

router = APIRouter()


@router.post("/send", response_model=MessageResponse)
async def send_message(
    msg_in: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a message to another user."""
    # Verify receiver exists
    result = await db.execute(select(User).filter(User.id == msg_in.receiver_id))
    receiver = result.scalars().first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")

    new_msg = Message(
        sender_id=current_user.id,
        receiver_id=receiver.id,
        content=msg_in.content
    )
    db.add(new_msg)
    await db.commit()
    await db.refresh(new_msg)
    return new_msg


@router.get("/{user_id}", response_model=List[MessageResponse])
async def get_chat_history(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve the full chat history between the current user and another user."""
    # Use explicit and_() / or_() to avoid operator precedence issues
    stmt = select(Message).filter(
        or_(
            and_(Message.sender_id == current_user.id, Message.receiver_id == user_id),
            and_(Message.sender_id == user_id, Message.receiver_id == current_user.id)
        )
    ).order_by(Message.created_at.asc())
    
    result = await db.execute(stmt)
    messages = result.scalars().all()
    return list(messages)
