from pydantic import BaseModel, EmailStr, field_validator


# -----------------------
# Register (Email + Password)
# -----------------------
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        if len(value) > 72:
            raise ValueError("Password must be at most 72 characters")
        if not any(c.isalpha() for c in value):
            raise ValueError("Password must contain at least one letter")
        if not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one number")
        return value


# -----------------------
# Login (Email + Password)
# -----------------------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# -----------------------
# Google OAuth Login
# -----------------------
class GoogleLoginRequest(BaseModel):
    id_token: str


# -----------------------
# Auth Responses
# -----------------------
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    email: EmailStr


class AuthResponse(BaseModel):
    user_id: str
    email: EmailStr
    provider: str
