from uuid import UUID

from fastapi import APIRouter, Depends, status

from kordevance.application.dependencies.auth import require_paired_device
from kordevance.application.dependencies.deps import get_profile_timezone
from kordevance.application.dependencies.profile_management import (
    CreateProfileUseCaseDep,
    DeleteProfileUseCaseDep,
    GetProfilesUseCaseDep,
    GetProfileUseCaseDep,
    UpdateProfileUseCaseDep,
)
from kordevance.application.schemas.profile import CreateProfileRequest, ProfileResponse, UpdateProfileRequest
from kordevance.domain.use_cases.profile_management.request_models import CreateProfileRequest as Crp
from kordevance.domain.use_cases.profile_management.request_models import UpdateProfileRequest as Udp

router: APIRouter = APIRouter(prefix="/profiles", tags=["profiles"], dependencies=[Depends(require_paired_device)])


@router.post("", response_model=ProfileResponse)
async def create_profile(
    body: CreateProfileRequest,
    service: CreateProfileUseCaseDep,
    profile_timezone: str = Depends(get_profile_timezone),
) -> ProfileResponse:
    request = Crp(name=body.name, timezone=profile_timezone)
    profile = await service.execute(request)
    return ProfileResponse(id=profile.id, name=profile.name)


@router.patch("")
async def update_profile(
    body: UpdateProfileRequest,
    service: UpdateProfileUseCaseDep,
) -> None:
    await service.execute(Udp(profile_id=body.id, name=body.name, home_timezone=body.home_timezone))


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(id: UUID, service: DeleteProfileUseCaseDep) -> None:
    await service.execute(id)


@router.get("/{id}", response_model=ProfileResponse)
async def get_profile(id: UUID, service: GetProfileUseCaseDep) -> ProfileResponse:
    profile = await service.execute(id)
    return ProfileResponse(id=profile.id, name=profile.name)


@router.get("", response_model=list[ProfileResponse])
async def get_all_profiles(service: GetProfilesUseCaseDep) -> list[ProfileResponse]:
    profiles = await service.execute()
    return [ProfileResponse(id=profile.id, name=profile.name) for profile in profiles]
