from abc import ABC, abstractmethod

from kordevance.domain.models.connectors import AvailableConnectors, Connector
from kordevance.domain.models.device import Device


class ProxyRelayClient(ABC):
    @abstractmethod
    async def register_device(self) -> Device: ...
    @abstractmethod
    async def get_connections(self, device: Device) -> list[Connector]: ...
    @abstractmethod
    async def get_available_connectors(self, device: Device) -> list[AvailableConnectors]: ...
