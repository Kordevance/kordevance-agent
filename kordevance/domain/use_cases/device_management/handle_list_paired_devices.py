from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.models.paired_device import PairedDevice
from kordevance.domain.services.pairing_service import PairingService


class HandleListPairedDevices(UseCase[None, list[PairedDevice]]):
    def __init__(self, pairing_service: PairingService) -> None:
        self._pairing_service: PairingService = pairing_service

    async def execute(self, request: None = None) -> list[PairedDevice]:
        return await self._pairing_service.list_devices()
