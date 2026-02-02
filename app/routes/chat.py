# Delete a chat session and its messages
from fastapi import status
from sqlalchemy import delete as sqlalchemy_delete

# List all chat sessions (for sidebar)
from fastapi import HTTPException
from sqlalchemy import asc
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from pydantic import BaseModel

from app.db.database import get_db
from app.db.models import ChatSession, ChatMessage
from app.schemas import ChatStartResponse

from app.llms.gemini_mock import ask_gemini
from app.llms.deepseek_chat_mock import ask_deepseek_chat
from app.llms.deepseek_coder_mock import ask_deepseek_coder

router = APIRouter(prefix="/chat", tags=["chat"])

@router.get("/sessions")
async def list_chat_sessions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ChatSession).order_by(ChatSession.created_at.desc())
    )
    sessions = result.scalars().all()
    # Optionally, fetch the first message for preview
    session_list = []
    for s in sessions:
        msg_result = await db.execute(
            select(ChatMessage).where(ChatMessage.session_id == s.id).order_by(ChatMessage.created_at.asc())
        )
        first_msg = msg_result.scalars().first()
        session_list.append({
            "session_id": str(s.id),
            "mode": s.mode,
            "createdAt": s.created_at.isoformat() if s.created_at else None,
            "selectedLlm": s.selected_llm,
            "firstMessage": first_msg.content if first_msg else None
        })
    return session_list

# Fetch chat history for a session
@router.get("/history/{session_id}")
async def get_chat_history(session_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(asc(ChatMessage.created_at))
    )
    messages = result.scalars().all()
    if not messages:
        return []
    # Return all messages with selected_llm info
    return [
        {
            "id": str(m.id),
            "role": m.role,
            "content": m.content,
            "createdAt": m.created_at.isoformat() if m.created_at else None,
            "llm_type": m.llm_type,
            "selected_llm": m.selected_llm
        }
        for m in messages
    ]


@router.post("/start", response_model=ChatStartResponse)
async def start_chat(
    db: AsyncSession = Depends(get_db),
):
    session = ChatSession(
        mode="MULTI",
        selected_llm=None,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    return {
        "session_id": session.id,
        "mode": session.mode,
    }


# Request body model for /multi
class MultiLLMChatRequest(BaseModel):
    session_id: UUID
    prompt: str
    llm: str | None = None  # Optional: 'gemini', 'deepseek_chat', 'deepseek_coder'

@router.post("/multi")
async def multi_llm_chat(
    payload: MultiLLMChatRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.id == payload.session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        return {"error": "Invalid session"}

    responses = []
    selected_llm = payload.llm if payload.llm else None
    # Store the user prompt as a ChatMessage
    user_msg = ChatMessage(
        session_id=payload.session_id,
        llm_type='user',
        role='user',
        content=payload.prompt,
        selected_llm=selected_llm
    )
    db.add(user_msg)
    await db.commit()
    # Now generate and store assistant responses
    if payload.llm == 'gemini':
        gemini = ask_gemini(payload.prompt, [])
        responses.append({"llm": "gemini", "response": gemini})
        db.add(ChatMessage(
            session_id=payload.session_id,
            llm_type='gemini',
            role='assistant',
            content=gemini,
            selected_llm=selected_llm
        ))
    elif payload.llm == 'deepseek_chat':
        deepseek_chat = ask_deepseek_chat(payload.prompt, [])
        responses.append({"llm": "deepseek-chat", "response": deepseek_chat})
        db.add(ChatMessage(
            session_id=payload.session_id,
            llm_type='deepseek_chat',
            role='assistant',
            content=deepseek_chat,
            selected_llm=selected_llm
        ))
    elif payload.llm == 'deepseek_coder':
        deepseek_coder = ask_deepseek_coder(payload.prompt, [])
        responses.append({"llm": "deepseek-coder", "response": deepseek_coder})
        db.add(ChatMessage(
            session_id=payload.session_id,
            llm_type='deepseek_coder',
            role='assistant',
            content=deepseek_coder,
            selected_llm=selected_llm
        ))
    else:
        gemini = ask_gemini(payload.prompt, [])
        deepseek_chat = ask_deepseek_chat(payload.prompt, [])
        deepseek_coder = ask_deepseek_coder(payload.prompt, [])
        responses = [
            {"llm": "gemini", "response": gemini},
            {"llm": "deepseek-chat", "response": deepseek_chat},
            {"llm": "deepseek-coder", "response": deepseek_coder},
        ]
        db.add(ChatMessage(
            session_id=payload.session_id,
            llm_type='gemini',
            role='assistant',
            content=gemini,
            selected_llm=None
        ))
        db.add(ChatMessage(
            session_id=payload.session_id,
            llm_type='deepseek_chat',
            role='assistant',
            content=deepseek_chat,
            selected_llm=None
        ))
        db.add(ChatMessage(
            session_id=payload.session_id,
            llm_type='deepseek_coder',
            role='assistant',
            content=deepseek_coder,
            selected_llm=None
        ))
    await db.commit()
    return {"responses": responses}

# Delete a chat session and all its messages
@router.delete("/delete/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_session(session_id: UUID, db: AsyncSession = Depends(get_db)):
    # Delete all messages for this session
    await db.execute(
        sqlalchemy_delete(ChatMessage).where(ChatMessage.session_id == session_id)
    )
    # Delete the session itself
    result = await db.execute(
        sqlalchemy_delete(ChatSession).where(ChatSession.id == session_id)
    )
    await db.commit()
    return
