import logging

from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.models.device import Device
from kordevance.domain.ports.credential_manager import CredManager
from kordevance.domain.ports.proxy_relay_client import ProxyRelayClient
from kordevance.domain.services.device_service import DeviceService


class HandleEnsureDeviceRegistered(UseCase[None, Device]):
    def __init__(self, credential_manager: CredManager, proxy_relay_client: ProxyRelayClient) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._service: DeviceService = DeviceService(store=credential_manager)
        self._proxy_relay_client: ProxyRelayClient = proxy_relay_client

    async def execute(self, request: None = None) -> Device:
        device = self._service.get_device_details()
        if device is not None:
            self._logger.info("Reusing existing device credentials")
            return device

        self._logger.info("No device credentials found, registering a new device with ProxyRelay")
        device = await self._proxy_relay_client.register_device()
        self._service.save_device_details(device_id=device.id, device_secret=device.secret)
        return device
