from uuid import UUID

from pydantic import BaseModel

from kordevance.domain.models.chat_turn import ChatTurn


class Conversation(BaseModel):
    id: UUID
    messages: list[ChatTurn]
