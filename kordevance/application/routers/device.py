from uuid import UUID

from fastapi import APIRouter, Depends, status

from kordevance.application.dependencies.auth import require_owner_device
from kordevance.application.dependencies.pairing import (
    CreatePairingInviteUseCaseDep,
    ListPairedDevicesUseCaseDep,
    PromotePairedDeviceUseCaseDep,
    RegisterDeviceUseCaseDep,
)
from kordevance.application.schemas.device import (
    PairedDeviceResponse,
    PairingInviteResponse,
    RegisterDeviceRequest,
    RegisterDeviceResponse,
)
from kordevance.domain.models.paired_device import PairedDevice

router: APIRouter = APIRouter(prefix="/device", tags=["device"])


@router.post("/register", status_code=status.HTTP_200_OK)
async def register_device(body: RegisterDeviceRequest, service: RegisterDeviceUseCaseDep) -> RegisterDeviceResponse:
    token = await service.execute(body.code)
    return RegisterDeviceResponse(token=token)


@router.post("/pairing/invites", status_code=status.HTTP_201_CREATED)
async def create_pairing_invite(
    service: CreatePairingInviteUseCaseDep, _: PairedDevice = Depends(require_owner_device)
) -> PairingInviteResponse:
    code = await service.execute()
    return PairingInviteResponse(code=code)


@router.get("/pairing/devices", response_model=list[PairedDeviceResponse])
async def list_paired_devices(
    service: ListPairedDevicesUseCaseDep, _: PairedDevice = Depends(require_owner_device)
) -> list[PairedDeviceResponse]:
    devices = await service.execute()
    return [PairedDeviceResponse(id=d.id, is_owner=d.is_owner, created_at=d.created_at) for d in devices]


@router.post("/pairing/devices/{device_id}/promote", status_code=status.HTTP_204_NO_CONTENT)
async def promote_paired_device(
    device_id: UUID, service: PromotePairedDeviceUseCaseDep, _: PairedDevice = Depends(require_owner_device)
) -> None:
    await service.execute(device_id)
