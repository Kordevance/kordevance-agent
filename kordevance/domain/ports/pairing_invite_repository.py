from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from kordevance.domain.models.pairing_invite import PairingInvite


class PairingInviteRepo(ABC):
    @abstractmethod
    async def create(self, code_hash: str, expires_at: datetime) -> None: ...
    @abstractmethod
    async def fetch_live(self) -> list[PairingInvite]: ...
    @abstractmethod
    async def delete(self, invite_id: UUID) -> None: ...
    @abstractmethod
    async def delete_all(self) -> None: ...
