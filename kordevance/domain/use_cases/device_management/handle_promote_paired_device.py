from uuid import UUID

from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.services.pairing_service import PairingService


class HandlePromotePairedDevice(UseCase[UUID, None]):
    def __init__(self, pairing_service: PairingService) -> None:
        self._pairing_service: PairingService = pairing_service

    async def execute(self, request: UUID) -> None:
        await self._pairing_service.promote(request)
