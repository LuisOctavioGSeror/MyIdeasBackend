from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from app.utils.enums import StatusEnum

class UserBase(BaseModel):
    email: str
    full_name: str
    status: Optional[str] = None

class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    status: Optional[str] = None

class User(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
