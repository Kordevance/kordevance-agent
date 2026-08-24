from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID


class MessageStore(ABC):
    """Persists conversation turns as pre-serialized JSON strings"""

    @abstractmethod
    async def append(self, profile_id: UUID, conversation_id: UUID, message_json: str, timestamp: datetime) -> None:
        """Append one already-serialized turn to the conversation's history."""
        ...

    @abstractmethod
    async def load_history(self, profile_id: UUID, conversation_id: UUID) -> list[tuple[str, datetime]]:
        """Return every previously appended turn for this conversation, oldest first."""
        ...

    @abstractmethod
    async def list_conversations(self, profile_id: UUID) -> list[UUID]:
        """Return the ids of every conversation recorded for this profile so far."""
        ...
