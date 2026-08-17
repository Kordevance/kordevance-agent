from abc import ABC, abstractmethod

from kordevance.domain.models.device import Device


class ProxyRelayClient(ABC):
    @abstractmethod
    async def register_device(self) -> Device: ...
