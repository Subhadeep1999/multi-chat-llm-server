import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.database import Base


# =========================
# User Model (LOCAL + GOOGLE)
# =========================
class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "chat_app"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    email = Column(String, unique=True, nullable=False, index=True)

    # Nullable for Google users
    password_hash = Column(String, nullable=True)

    # local | google
    provider = Column(String, nullable=False, default="local")

    created_at = Column(DateTime(timezone=True), server_default=func.now())


# =========================
# Chat Session
# =========================
class ChatSession(Base):
    __tablename__ = "chat_session"
    __table_args__ = {"schema": "chat_app"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

        # user_id removed: no user dependency

    mode = Column(String, nullable=False)  # MULTI | SINGLE
    selected_llm = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


# =========================
# Chat Messages
# =========================
class ChatMessage(Base):
    __tablename__ = "chat_message"
    __table_args__ = {"schema": "chat_app"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chat_app.chat_session.id"),
        nullable=False
    )

    llm_type = Column(String, nullable=False)
    selected_llm = Column(String, nullable=True)  # stores which LLM was selected for this prompt, if any
    role = Column(String, nullable=False)  # user | assistant
    content = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
