from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.services.pairing_service import PairingService


class HandleCreatePairingInvite(UseCase[None, str]):
    def __init__(self, pairing_service: PairingService) -> None:
        self._pairing_service: PairingService = pairing_service

    async def execute(self, request: None = None) -> str:
        return await self._pairing_service.create_invite()
