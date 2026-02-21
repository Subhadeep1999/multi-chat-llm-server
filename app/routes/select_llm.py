from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from uuid import UUID
from app.db.database import get_db
from app.db.models import ChatMessage
from pydantic import BaseModel

router = APIRouter()

from typing import Optional

class SelectLlmRequest(BaseModel):
    session_id: UUID
    llm: Optional[str] = None

@router.post("/chat/select-llm")
async def select_llm(
    payload: SelectLlmRequest,
    db: AsyncSession = Depends(get_db),
):
    # Find the latest user message for this session
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == payload.session_id, ChatMessage.role == 'user')
        .order_by(desc(ChatMessage.created_at))
        .limit(1)
    )
    user_msg = result.scalar_one_or_none()
    if not user_msg:
        raise HTTPException(status_code=404, detail="No user message found for this session.")
    user_msg.selected_llm = payload.llm
    await db.commit()
    return {"status": "ok"}
