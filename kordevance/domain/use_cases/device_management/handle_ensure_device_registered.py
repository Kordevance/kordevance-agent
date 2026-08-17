import logging

from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.models.device import Device
from kordevance.domain.ports.credential_manager import CredManager
from kordevance.domain.ports.proxy_relay_client import ProxyRelayClient
from kordevance.domain.use_cases.device_management.handle_fetch_device_details import HandleFetchDeviceDetails
from kordevance.domain.use_cases.device_management.handle_persist_device_details import HandlePersistDeviceDetails
from kordevance.domain.use_cases.device_management.request_models import SaveDeviceDetailsRequest


class HandleEnsureDeviceRegistered(UseCase[None, Device]):
    def __init__(self, credential_manager: CredManager, proxy_relay_client: ProxyRelayClient) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._fetch_device_details: HandleFetchDeviceDetails = HandleFetchDeviceDetails(
            credential_manager=credential_manager
        )
        self._persist_device_details: HandlePersistDeviceDetails = HandlePersistDeviceDetails(
            credential_manager=credential_manager
        )
        self._proxy_relay_client: ProxyRelayClient = proxy_relay_client

    async def execute(self, request: None = None) -> Device:
        device = await self._fetch_device_details.execute()
        if device is not None:
            self._logger.info("Reusing existing device credentials")
            return device

        self._logger.info("No device credentials found, registering a new device with ProxyRelay")
        device = await self._proxy_relay_client.register_device()
        await self._persist_device_details.execute(
            SaveDeviceDetailsRequest(device_id=device.id, device_secret=device.secret)
        )
        return device
