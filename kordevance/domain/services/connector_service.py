import logging

from kordevance.domain.models.connectors import Connector
from kordevance.domain.ports.credential_manager import CredManager
from kordevance.domain.ports.proxy_relay_client import ProxyRelayClient
from kordevance.domain.services.device_service import DeviceService


class ConnectorService:
    def __init__(self, credential_manager: CredManager, proxy_relay_client: ProxyRelayClient) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._device_service: DeviceService = DeviceService(store=credential_manager)
        self._relay_client: ProxyRelayClient = proxy_relay_client

    async def get_connectors(self) -> list[Connector]:
        device = self._device_service.get_current_device()
        relay_connectors = await self._relay_client.get_connections(device)
        available_connectors = await self._relay_client.get_available_connectors(device)

        combined: dict[tuple[str, str], Connector] = {}
        relay_providers: set[str] = set()

        for connector in relay_connectors:
            combined[(connector.provider, connector.category)] = connector
            relay_providers.add(connector.provider)

        for available in available_connectors:
            if available.provider in relay_providers:
                continue
            for category in available.categories:
                key = (available.provider, category)
                combined.setdefault(
                    key,
                    Connector(
                        provider=available.provider,
                        category=category,
                        icon=available.icon,
                        active=False,
                    ),
                )

        return list(combined.values())
