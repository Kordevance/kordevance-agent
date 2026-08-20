from typing import Any
from uuid import UUID

import httpx

from kordevance.domain.models.connectors import AvailableConnectors, Connector
from kordevance.domain.models.device import Device
from kordevance.domain.models.tool import ToolDefinition
from kordevance.domain.ports.proxy_relay_client import ProxyRelayClient
from kordevance.exceptions import ConnectionMissingError, ItemNotFoundError


class HttpProxyRelayClient(ProxyRelayClient):
    def __init__(self, base_url: str) -> None:
        self._base_url: str = base_url.rstrip("/")

    async def register_device(self) -> Device:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(f"{self._base_url}/devices/register")
            response.raise_for_status()
            payload = response.json()
            return Device(id=payload["device_id"], secret=payload["secret"])

    async def get_connections(self, device: Device) -> list[Connector]:
        headers = {"X-Device-Id": device.id, "X-Device-Secret": device.secret}
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(f"{self._base_url}/connections/sessions", headers=headers)
            response.raise_for_status()
            payload = response.json()

            return [
                Connector(provider=entry["provider"], category=entry["integration"], active=entry["status_ok"])
                for entry in payload
            ]

    async def get_available_connectors(self, device: Device) -> list[AvailableConnectors]:
        headers = {"X-Device-Id": device.id, "X-Device-Secret": device.secret}
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(f"{self._base_url}/connectors/", headers=headers)
            response.raise_for_status()
            payload = response.json()

            return [
                AvailableConnectors(provider=entry["provider"], categories=entry["categories"], icon=entry["icon_url"])
                for entry in payload
            ]

    async def register_connector(self, device: Device, profile_id: UUID, provider: str, category: str) -> str:
        headers = {"X-Device-Id": device.id, "X-Device-Secret": device.secret}
        async with httpx.AsyncClient(timeout=15.0) as client:
            payload = {"integration": category, "provider": provider, "profile_id": profile_id}
            response = await client.post(f"{self._base_url}/connections/session", headers=headers, json=payload)
            response.raise_for_status()
            return response.text

    async def delete_connector(self, device: Device, profile_id: UUID, provider: str, category: str) -> None:
        headers = {"X-Device-Id": device.id, "X-Device-Secret": device.secret}
        async with httpx.AsyncClient(timeout=15.0) as client:
            payload: dict[str, Any] = {"integration": category, "provider": provider, "profile_id": profile_id}
            response = await client.delete(f"{self._base_url}/connections/session", headers=headers, params=payload)
            response.raise_for_status()

    async def get_available_tools(self, device: Device, profile_id: UUID) -> list[ToolDefinition]:
        headers = {"X-Device-Id": device.id, "X-Device-Secret": device.secret}
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{self._base_url}/tools", headers=headers, params={"profileId": str(profile_id)}
            )
            response.raise_for_status()
            payload = response.json()

            return [
                ToolDefinition(
                    name=entry["name"],
                    description=entry["description"],
                    provider=entry["provider"],
                    category=entry["category"],
                    requires_confirmation=entry["requires_confirmation"],
                    input_schema=entry["input_schema"],
                )
                for entry in payload
            ]

    async def execute_tool(
        self, device: Device, profile_id: UUID, tool_name: str, tool_input: dict[str, Any]
    ) -> Any:
        headers = {"X-Device-Id": device.id, "X-Device-Secret": device.secret}
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {"profile_id": str(profile_id), "tool_name": tool_name, "input": tool_input}
            response = await client.post(f"{self._base_url}/tools/execute", headers=headers, json=payload)

            if response.status_code == httpx.codes.NOT_FOUND:
                raise ItemNotFoundError(f"No tool named '{tool_name}' is available")
            if response.status_code == httpx.codes.CONFLICT:
                raise ConnectionMissingError(
                    f"No valid connection for tool '{tool_name}'; (re)authorize it via connections/session"
                )
            response.raise_for_status()

            return response.json()
