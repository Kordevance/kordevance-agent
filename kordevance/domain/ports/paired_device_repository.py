from abc import ABC, abstractmethod
from uuid import UUID

from kordevance.domain.models.paired_device import PairedDevice


class PairedDeviceRepo(ABC):
    @abstractmethod
    async def exists_any(self) -> bool: ...
    @abstractmethod
    async def create(self, token_hash: str, is_owner: bool) -> PairedDevice: ...
    @abstractmethod
    async def get_by_token_hash(self, token_hash: str) -> PairedDevice | None: ...
    @abstractmethod
    async def fetch_all(self) -> list[PairedDevice]: ...
    @abstractmethod
    async def set_owner(self, device_id: UUID, is_owner: bool) -> None: ...
