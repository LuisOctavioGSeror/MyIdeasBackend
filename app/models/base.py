from sqlalchemy.orm import DeclarativeBase
from pydantic import BaseModel, ConfigDict


class Base(DeclarativeBase):
    pass


class PydanticBaseModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)