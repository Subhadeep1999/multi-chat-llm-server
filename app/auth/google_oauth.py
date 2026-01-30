from google.oauth2 import id_token
from google.auth.transport import requests
from fastapi import HTTPException
import os


GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")


def verify_google_token(token: str) -> dict:
    try:
        payload = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )
        return payload
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid Google token"
        )
