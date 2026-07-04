"""PhishGuard AI — Auth Schemas"""
from pydantic import BaseModel, Field, EmailStr


class UserRegister(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field("", max_length=255)


class UserLogin(BaseModel):
    email: str = Field(..., min_length=5)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserProfile"


class UserProfile(BaseModel):
    id: str
    email: str
    username: str
    full_name: str
    role: str
    created_at: str


class APIKeyCreate(BaseModel):
    name: str = Field("default", max_length=100)


class APIKeyResponse(BaseModel):
    id: str
    name: str
    key_prefix: str
    created_at: str
    last_used: str = ""
    key: str = ""  # Only populated on creation


TokenResponse.model_rebuild()
