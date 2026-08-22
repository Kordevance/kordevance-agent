from abc import ABC, abstractmethod
from uuid import UUID

from kordevance.domain.models.chat_turn import ChatTurn


class ChatOrchestrator(ABC):
    @abstractmethod
    async def handle_message(self, profile_id: UUID, conversation_id: UUID, message: str) -> str: ...

    @abstractmethod
    async def get_history(self, profile_id: UUID, conversation_id: UUID) -> list[ChatTurn]: ...
