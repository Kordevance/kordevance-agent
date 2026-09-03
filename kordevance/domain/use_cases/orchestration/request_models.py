from uuid import UUID

from pydantic import BaseModel


class ChatOrchestrationRequest(BaseModel):
    profile_id: UUID
    conversation_id: UUID
    message: str
    timezone: str | None = None
