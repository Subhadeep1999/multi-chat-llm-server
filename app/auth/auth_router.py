from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.db.database import get_db
from app.db.models import User
from app.auth.auth_schemas import (
    RegisterRequest,
    LoginRequest,
    GoogleLoginRequest,
    TokenResponse,
    UserResponse
)
from app.auth.auth_utils import hash_password, verify_password
from app.core.security import create_access_token
from app.auth.google_oauth import verify_google_token
from app.db.crud import create_user_session, delete_user_session_by_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        id=uuid.uuid4(),
        email=payload.email,
        password_hash=hash_password(payload.password),
        provider="local"
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Create token after registration
    token = create_access_token({"sub": str(user.id), "email": user.email})
    await create_user_session(db, str(user.id), token)
    return {"access_token": token}


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")

    token = create_access_token({"sub": str(user.id), "email": user.email})
    await create_user_session(db, str(user.id), token)
    return {"access_token": token}


@router.post("/google", response_model=TokenResponse)
async def google_login(
    payload: GoogleLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    google_user = verify_google_token(payload.id_token)
    email = google_user.get("email")

    if not email:
        raise HTTPException(400, "Google account has no email")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            id=uuid.uuid4(),
            email=email,
            password_hash="GOOGLE_OAUTH",
            provider="google"
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    token = create_access_token({"sub": str(user.id), "email": user.email})
    await create_user_session(db, str(user.id), token)
    return {"access_token": token}


@router.post("/logout")
async def logout(request: Request, db: AsyncSession = Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid token")
    token = auth_header.split(" ", 1)[1]
    await delete_user_session_by_token(db, token)
    return {"detail": "Logged out successfully"}
