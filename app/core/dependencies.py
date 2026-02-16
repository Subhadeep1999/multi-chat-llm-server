from fastapi import Depends, HTTPException, status, Request
from jose import jwt, JWTError
from app.db.crud import get_user_session_by_token
from app.core.security import SECRET_KEY, ALGORITHM
from app.db.database import get_db

async def get_current_user_session(request: Request, db=Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing or invalid token")
    token = auth_header.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
    session = await get_user_session_by_token(db, token)
    if not session:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token not found or expired")
    return session
