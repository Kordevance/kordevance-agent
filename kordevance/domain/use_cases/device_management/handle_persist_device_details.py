import logging

from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.ports.credential_manager import CredManager
from kordevance.domain.use_cases.device_management import _ID_KEY, _SECRET_KEY, _SERVICE
from kordevance.domain.use_cases.device_management.request_models import SaveDeviceDetailsRequest


class HandlePersistDeviceDetails(UseCase[SaveDeviceDetailsRequest, None]):
    def __init__(self, credential_manager: CredManager) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._credential_manager: CredManager = credential_manager

    async def execute(self, request: SaveDeviceDetailsRequest) -> None:
        self._logger.info("Saving device credentials")

        self._credential_manager.set(_SERVICE, _ID_KEY, request.device_id)
        self._credential_manager.set(_SERVICE, _SECRET_KEY, request.device_secret)
