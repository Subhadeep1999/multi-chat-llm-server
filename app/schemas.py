from pydantic import BaseModel
from uuid import UUID
from typing import Optional, Dict, Any, List


class WordAnalysis(BaseModel):
    total_words: int
    word_count: int
    top_5_words: List[Dict[str, Any]]


class MultiLLMResponse(BaseModel):
    gemini: str
    deepseek_chat: str
    deepseek_coder: str


class ChatStartRequest(BaseModel):
    user_id: Optional[str] = None


class ChatStartResponse(BaseModel):
    session_id: UUID
    mode: str


class ChatMultiRequest(BaseModel):
    session_id: UUID
    prompt: str


class ChatMultiResponse(BaseModel):
    session_id: UUID
    responses: Dict[str, str]


# -------- STEP 5 --------

class SelectLLMRequest(BaseModel):
    session_id: UUID
    llm: str  # gemini | deepseek_chat | deepseek_coder


class SelectLLMResponse(BaseModel):
    session_id: UUID
    mode: str
    selected_llm: str


class ChatSingleRequest(BaseModel):
    session_id: UUID
    prompt: str


class ChatSingleResponse(BaseModel):
    session_id: UUID
    llm: str
    response: str
