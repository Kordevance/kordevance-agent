from abc import ABC, abstractmethod
from uuid import UUID


class ChatOrchestrator(ABC):
    @abstractmethod
    async def handle_message(self, profile_id: UUID, conversation_id: UUID, message: str) -> str: ...
