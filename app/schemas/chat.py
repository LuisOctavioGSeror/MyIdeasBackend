from pydantic import BaseModel
from typing import List


class Message(BaseModel):
    role: str
    content: str


class ChatIn(BaseModel):
    messages: List[Message]
    provider: str | None = None
    model: str | None = None


class ChatOut(BaseModel):
    provider: str
    model: str
    answer: str