from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from kordevance.domain.models.connectors import AvailableConnectors, Connector
from kordevance.domain.models.device import Device
from kordevance.domain.models.tool import ToolDefinition


class ProxyRelayClient(ABC):
    @abstractmethod
    async def register_device(self) -> Device: ...
    @abstractmethod
    async def get_connections(self, device: Device, profile_id: UUID) -> list[Connector]: ...
    @abstractmethod
    async def get_available_connectors(self, device: Device) -> list[AvailableConnectors]: ...
    @abstractmethod
    async def register_connector(self, device: Device, profile_id: UUID, provider: str, category: str) -> str: ...
    @abstractmethod
    async def delete_connector(self, device: Device, profile_id: UUID, provider: str, category: str) -> None: ...
    @abstractmethod
    async def get_available_tools(self, device: Device, profile_id: UUID) -> list[ToolDefinition]: ...
    @abstractmethod
    async def execute_tool(
        self, device: Device, profile_id: UUID, tool_name: str, tool_input: dict[str, Any]
    ) -> Any: ...
