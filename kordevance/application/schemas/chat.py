from uuid import UUID

from pydantic import BaseModel


class ChatMessageRequest(BaseModel):
    conversation_id: UUID | None = None
    message: str


class ChatMessageResponse(BaseModel):
    conversation_id: UUID
    reply: str
