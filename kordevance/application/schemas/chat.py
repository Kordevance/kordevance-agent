from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from kordevance.domain.models.chat_turn import ChatTurn


class ChatMessageRequest(BaseModel):
    conversation_id: UUID | None = None
    message: str


class ChatMessageResponse(BaseModel):
    conversation_id: UUID
    reply: str


class ConversationResponse(BaseModel):
    id: UUID
    messages: list[ChatTurn]
    timestamp: datetime


class ConversationsResponse(BaseModel):
    conversations: list[ConversationResponse]
