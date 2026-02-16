import uuid
from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import ChatSession, ChatMessage, UserSession


# -----------------------------
# Chat Session
# -----------------------------
async def create_chat_session(
    db: AsyncSession,
    user_id: Optional[str] = None
):
    session = ChatSession(
        id=uuid.uuid4(),
        user_id=user_id,
        mode="MULTI",
        selected_llm=None
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def get_chat_session(
    db: AsyncSession,
    session_id: UUID
) -> Optional[ChatSession]:
    result = await db.execute(
        select(ChatSession).where(ChatSession.id == session_id)
    )
    return result.scalar_one_or_none()


async def select_llm_for_session(
    db: AsyncSession,
    session_id: UUID,
    llm: str
):
    session = await get_chat_session(db, session_id)
    if not session:
        return None

    session.mode = "SINGLE"
    session.selected_llm = llm
    await db.commit()
    await db.refresh(session)
    return session


# -----------------------------
# Messages
# -----------------------------
async def save_message(
    db: AsyncSession,
    session_id: UUID,
    llm_type: str,
    role: str,
    content: str
):
    message = ChatMessage(
        id=uuid.uuid4(),
        session_id=session_id,
        llm_type=llm_type,
        role=role,
        content=content
    )
    db.add(message)
    await db.commit()


async def get_chat_history(
    db: AsyncSession,
    session_id: UUID
) -> List[dict]:
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
    )

    messages = result.scalars().all()

    return [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]


async def get_llm_history(
    db: AsyncSession,
    session_id: UUID,
    llm: str
) -> List[dict]:
    result = await db.execute(
        select(ChatMessage)
        .where(
            ChatMessage.session_id == session_id,
            ChatMessage.llm_type.in_(["user", llm])
        )
        .order_by(ChatMessage.created_at)
    )

    messages = result.scalars().all()

    return [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]


# -----------------------------
# User Session (JWT Token Store)
# -----------------------------
async def create_user_session(db: AsyncSession, user_id: str, token: str):
    session = UserSession(
        id=uuid.uuid4(),
        user_id=user_id,
        token=token
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session

async def get_user_session_by_token(db: AsyncSession, token: str):
    result = await db.execute(
        select(UserSession).where(UserSession.token == token)
    )
    return result.scalar_one_or_none()

async def delete_user_session_by_token(db: AsyncSession, token: str):
    session = await get_user_session_by_token(db, token)
    if session:
        await db.delete(session)
        await db.commit()
