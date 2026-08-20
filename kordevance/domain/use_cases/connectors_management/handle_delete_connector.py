import logging

from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.ports.credential_manager import CredManager
from kordevance.domain.ports.proxy_relay_client import ProxyRelayClient
from kordevance.domain.services.connector_service import ConnectorService
from kordevance.domain.use_cases.connectors_management.request_models import ConnectorRequest


class HandleDeleteConnector(UseCase[ConnectorRequest, None]):
    def __init__(self, credential_manager: CredManager, proxy_relay_client: ProxyRelayClient) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._service: ConnectorService = ConnectorService(
            credential_manager=credential_manager, proxy_relay_client=proxy_relay_client
        )

    async def execute(self, request: ConnectorRequest) -> None:
        self._logger.info(f"Deleting connector {request.provider}-{request.category} for profile {request.profile_id}")
        return await self._service.unregister_connector(request.profile_id, request.provider, request.category)
