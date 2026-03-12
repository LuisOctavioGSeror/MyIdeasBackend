from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.utils.enums import IdeaStatusEnum


class IdeaBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[IdeaStatusEnum] = IdeaStatusEnum.OPEN
    image_url: Optional[str] = None


class IdeaCreate(IdeaBase):
    pass


class IdeaUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[IdeaStatusEnum] = None
    image_url: Optional[str] = None


class Idea(IdeaBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

