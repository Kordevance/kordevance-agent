import logging
from uuid import UUID

from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.models.connectors import Connector
from kordevance.domain.ports.credential_manager import CredManager
from kordevance.domain.ports.proxy_relay_client import ProxyRelayClient
from kordevance.domain.services.connector_service import ConnectorService


class HandleFetchConnectors(UseCase[UUID, list[Connector]]):
    def __init__(self, credential_manager: CredManager, proxy_relay_client: ProxyRelayClient) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._service: ConnectorService = ConnectorService(
            credential_manager=credential_manager, proxy_relay_client=proxy_relay_client
        )

    async def execute(self, profile_id: UUID) -> list[Connector]:
        self._logger.info(f"Fetching connectors for profile {profile_id}")
        return await self._service.get_connectors()
