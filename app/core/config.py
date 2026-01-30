from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # app/

class Settings(BaseSettings):
    APP_NAME: str = "Multi Chat LLM"

    SECRET_KEY: str = "CHANGE_ME_SUPER_SECRET"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    GOOGLE_CLIENT_ID: str

    class Config:
        env_file = BASE_DIR / ".env"
        extra = "ignore"


settings = Settings()
