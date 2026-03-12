from app.models.base import Base
from app.utils.enums import IdeaStatusEnum
from sqlalchemy import String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone
from typing import Optional
import uuid


class Idea(Base):
    __tablename__ = "ideas"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[IdeaStatusEnum] = mapped_column(Enum(IdeaStatusEnum), default=IdeaStatusEnum.OPEN)
    image_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="ideas")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

