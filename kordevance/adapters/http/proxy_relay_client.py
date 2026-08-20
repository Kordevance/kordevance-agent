import httpx

from kordevance.domain.models.connectors import Connector
from kordevance.domain.models.device import Device
from kordevance.domain.models.connectors import AvailableConnectors
from kordevance.domain.ports.proxy_relay_client import ProxyRelayClient


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
