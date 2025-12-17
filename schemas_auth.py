from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    nom_complet: str = Field(..., max_length=200)
    email: EmailStr
    role: Optional[str] = "client"
    telephone: Optional[str] = Field(None, max_length=20)


class UserCreate(UserBase):
    mot_de_passe: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    mot_de_passe: str


class UserResponse(UserBase):
    id: int
    statut: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

