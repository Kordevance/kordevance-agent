from abc import ABC, abstractmethod
from uuid import UUID

from kordevance.domain.models.profile import Profile


class ProfileRepo(ABC):
    @abstractmethod
    async def save(self, name: str) -> Profile: ...
    @abstractmethod
    async def delete(self, profile_id: UUID) -> None: ...
    @abstractmethod
    async def fetch(self, profile_id: UUID) -> Profile: ...
    @abstractmethod
    async def fetch_all(self) -> list[Profile]: ...

    @abstractmethod
    async def update(self, request: Profile) -> None: ...
