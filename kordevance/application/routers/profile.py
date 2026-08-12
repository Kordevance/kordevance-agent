from uuid import UUID

from fastapi import APIRouter

from kordevance.application.dependencies.profile_management import (
    CreateProfileUseCaseDep,
    DeleteProfileUseCaseDep,
    GetProfilesUseCaseDep,
    GetProfileUseCaseDep,
    UpdateProfileUseCaseDep,
)
from kordevance.application.schemas.profile import CreateProfileRequest, ProfileResponse, UpdateProfileRequest
from kordevance.domain.models.profile import Profile
from kordevance.exceptions import BadRequestError

router: APIRouter = APIRouter(prefix="/profiles", tags=["profiles"])


def _parse_id(id: str) -> UUID | None:
    try:
        return UUID(id)
    except ValueError:
        return None


@router.post("", response_model=ProfileResponse)
async def create_profile(body: CreateProfileRequest, service: CreateProfileUseCaseDep) -> ProfileResponse:
    profile = await service.execute(body.name)
    return ProfileResponse(id=profile.id, name=profile.name)


@router.patch("")
async def update_profile(body: UpdateProfileRequest, service: UpdateProfileUseCaseDep) -> None:
    await service.execute(Profile(id=body.id, name=body.name))


@router.delete("/{id}")
async def delete_profile(id: str, service: DeleteProfileUseCaseDep) -> None:
    profile_id = _parse_id(id)
    if profile_id is None:
        raise BadRequestError("Query parameter ID must be a valid UUID")

    await service.execute(profile_id)


@router.get("/{id}", response_model=ProfileResponse)
async def get_profile(id: str, service: GetProfileUseCaseDep) -> ProfileResponse:
    profile_id = _parse_id(id)
    if profile_id is None:
        raise BadRequestError("Query parameter ID must be a valid UUID")

    profile = await service.execute(profile_id)
    return ProfileResponse(id=profile.id, name=profile.name)


@router.get("", response_model=list[ProfileResponse])
async def get_all_profiles(service: GetProfilesUseCaseDep) -> list[ProfileResponse]:
    profiles = await service.execute()
    return [ProfileResponse(id=profile.id, name=profile.name) for profile in profiles]
