import logging

from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.models.device import Device
from kordevance.domain.ports.credential_manager import CredManager
from kordevance.domain.use_cases.device_management import _ID_KEY, _SECRET_KEY, _SERVICE


class HandleFetchDeviceDetails(UseCase[None, Device | None]):
    def __init__(self, credential_manager: CredManager) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._credential_manager: CredManager = credential_manager

    async def execute(self, request: None = None) -> Device | None:
        self._logger.info("Fetching device credentials")

        device_id = self._credential_manager.get(_SERVICE, _ID_KEY)
        device_secret = self._credential_manager.get(_SERVICE, _SECRET_KEY)

        if device_id is None or device_secret is None:
            self._logger.error("Device credentials invalid")
            return None

        return Device(id=device_id, secret=device_secret)
