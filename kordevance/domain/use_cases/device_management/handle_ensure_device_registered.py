import logging

from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.models.device import Device
from kordevance.domain.ports.credential_manager import CredManager
from kordevance.domain.ports.device_registration_repository import DeviceRegistrationRepo
from kordevance.domain.ports.proxy_relay_client import ProxyRelayClient
from kordevance.domain.services.device_service import DeviceService
from kordevance.exceptions import DeviceCredentialsLostError


class HandleEnsureDeviceRegistered(UseCase[None, Device]):
    def __init__(
        self,
        credential_manager: CredManager,
        proxy_relay_client: ProxyRelayClient,
        device_registration_repo: DeviceRegistrationRepo,
    ) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._service: DeviceService = DeviceService(store=credential_manager)
        self._proxy_relay_client: ProxyRelayClient = proxy_relay_client
        self._registration_repo: DeviceRegistrationRepo = device_registration_repo

    async def execute(self, request: None = None) -> Device:
        device = self._service.get_device_details()
        if device is not None:
            self._logger.info("Reusing existing device credentials")
            return device

        registration = await self._registration_repo.get()
        if registration is not None:
            # This installation registered before (device_id recorded in the DB), but the keyring no
            # longer has the matching credentials. This is never a legitimate "first boot" state, so
            # refuse to silently mint a new device identity.
            self._logger.error(
                "Device credentials are missing from secure storage, but this installation already "
                "registered device_id=%s at %s. Refusing to re-register.",
                registration.device_id,
                registration.registered_at,
            )
            raise DeviceCredentialsLostError(
                f"Device credentials for previously registered device_id={registration.device_id} are "
                "missing from secure storage. This installation cannot recover automatically; reinstall."
            )

        self._logger.info("No prior device registration found, registering a new device with ProxyRelay")
        device = await self._proxy_relay_client.register_device()
        self._service.save_device_details(device_id=device.id, device_secret=device.secret)
        await self._registration_repo.save(device_id=device.id)
        return device
