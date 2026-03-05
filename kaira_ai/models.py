from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    name: str
    email: EmailStr
    profile_image: str | None = None
    role: str = "user"

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

from enum import Enum
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
