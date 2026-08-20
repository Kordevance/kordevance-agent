from abc import ABC, abstractmethod
from uuid import UUID

from kordevance.domain.models.event import Event


class EventRepo(ABC):
    @abstractmethod
    async def save(self, event: Event) -> None: ...
    @abstractmethod
    async def fetch(self, profile_id: UUID, event_id: UUID) -> Event: ...
    @abstractmethod
    async def fetch_all_for_goal(self, profile_id: UUID, goal_id: UUID) -> list[Event]: ...
    @abstractmethod
    async def update(self, event: Event) -> None: ...
