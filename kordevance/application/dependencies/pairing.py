from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from kordevance.adapters.secret_store.claim_code_store import FileClaimCodeStore
from kordevance.adapters.sql_store.paired_device_repository import PairedDeviceRepository
from kordevance.adapters.sql_store.pairing_invite_repository import PairingInviteRepository
from kordevance.application import _WORKING_DIRECTORY
from kordevance.application.dependencies.sql_store_adapter import get_engine
from kordevance.domain.services.pairing_service import PairingService
from kordevance.domain.use_cases.device_management.handle_create_pairing_invite import HandleCreatePairingInvite
from kordevance.domain.use_cases.device_management.handle_list_paired_devices import HandleListPairedDevices
from kordevance.domain.use_cases.device_management.handle_promote_paired_device import HandlePromotePairedDevice
from kordevance.domain.use_cases.device_management.handle_register_device import HandleRegisterDevice

_CLAIM_CODE_PATH = _WORKING_DIRECTORY.joinpath("claim_code")


@lru_cache(maxsize=1)
def get_pairing_service() -> PairingService:
    return PairingService(
        paired_device_repo=PairedDeviceRepository(get_engine()),
        pairing_invite_repo=PairingInviteRepository(get_engine()),
        claim_code_store=FileClaimCodeStore(_CLAIM_CODE_PATH),
    )


def get_register_device_use_case() -> HandleRegisterDevice:
    return HandleRegisterDevice(pairing_service=get_pairing_service())


def get_create_pairing_invite_use_case() -> HandleCreatePairingInvite:
    return HandleCreatePairingInvite(pairing_service=get_pairing_service())


def get_list_paired_devices_use_case() -> HandleListPairedDevices:
    return HandleListPairedDevices(pairing_service=get_pairing_service())


def get_promote_paired_device_use_case() -> HandlePromotePairedDevice:
    return HandlePromotePairedDevice(pairing_service=get_pairing_service())


RegisterDeviceUseCaseDep = Annotated[HandleRegisterDevice, Depends(get_register_device_use_case)]
CreatePairingInviteUseCaseDep = Annotated[HandleCreatePairingInvite, Depends(get_create_pairing_invite_use_case)]
ListPairedDevicesUseCaseDep = Annotated[HandleListPairedDevices, Depends(get_list_paired_devices_use_case)]
PromotePairedDeviceUseCaseDep = Annotated[HandlePromotePairedDevice, Depends(get_promote_paired_device_use_case)]
