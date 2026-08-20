import logging

from kordevance.domain.models.device import Device
from kordevance.domain.ports.credential_manager import CredManager


class DeviceService:
    def __init__(self, store: CredManager) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._store: CredManager = store

        self.__SERVICE: str = "device"
        self.__ID_KEY: str = "device_id"
        self.__SECRET_KEY: str = "device_secret"  # noqa: S105

    def save_device_details(self, device_id: str, device_secret: str) -> None:
        self._logger.info("Saving device credentials")

        self._store.set(self.__SERVICE, self.__ID_KEY, device_id)
        self._store.set(self.__SERVICE, self.__SECRET_KEY, device_secret)

    def get_device_details(self) -> Device | None:
        self._logger.info("Fetching device credentials")

        device_id = self._store.get(self.__SERVICE, self.__ID_KEY)
        device_secret = self._store.get(self.__SERVICE, self.__SECRET_KEY)

        if device_id is None or device_secret is None:
            self._logger.error("Device credentials invalid")
            return None

        return Device(id=device_id, secret=device_secret)

    def get_current_device(self) -> Device:
        device = self.get_device_details()
        if device is None:
            raise ValueError("Could not load current device credentials")
        return device
