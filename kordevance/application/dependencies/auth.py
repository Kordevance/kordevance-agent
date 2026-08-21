from fastapi import Depends, Header

from kordevance.application.dependencies.pairing import get_pairing_service
from kordevance.domain.models.paired_device import PairedDevice
from kordevance.domain.services.pairing_service import PairingService
from kordevance.exceptions import UnauthorizedError


async def require_paired_device(
    authorization: str | None = Header(default=None),
    pairing_service: PairingService = Depends(get_pairing_service),
) -> PairedDevice:
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedError("Missing or malformed Authorization header")

    token = authorization.removeprefix("Bearer ")
    return await pairing_service.authenticate(token)


async def require_owner_device(device: PairedDevice = Depends(require_paired_device)) -> PairedDevice:
    if not device.is_owner:
        raise UnauthorizedError("Only the owner device can perform this action")
    return device
