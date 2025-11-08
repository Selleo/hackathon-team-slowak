from datetime import datetime

from pydantic import BaseModel, EmailStr, Field
from uuid import UUID

class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    accessToken: str
    tokenType: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    email: str
    username: str
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True

