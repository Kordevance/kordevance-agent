import httpx

from kordevance.domain.models.device import Device
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
