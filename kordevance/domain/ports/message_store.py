from abc import ABC, abstractmethod
from uuid import UUID


class MessageStore(ABC):
    """Persists conversation turns as pre-serialized JSON strings"""

    @abstractmethod
    async def append(self, profile_id: UUID, conversation_id: UUID, message_json: str) -> None:
        """Append one already-serialized turn to the conversation's history."""
        ...

    @abstractmethod
    async def load_history(self, profile_id: UUID, conversation_id: UUID) -> list[str]:
        """Return every previously appended turn for this conversation, oldest first."""
        ...
