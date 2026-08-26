from uuid import UUID

from fastapi import Depends, Header

from kordevance.application.dependencies.sql_store_adapter import get_profile_repository
from kordevance.application.schemas.profile import ProfileContext
from kordevance.application.utils import parse_id
from kordevance.domain.ports.profile_repository import ProfileRepo
from kordevance.exceptions import BadRequestError


async def get_profile_id(x_profile_id: str = Header(...)) -> UUID:
    if not x_profile_id:
        raise BadRequestError("Missing X-Profile-Id header")

    profile_id = parse_id(x_profile_id)
    if profile_id is None:
        raise BadRequestError("X-Profile-Id must be a valid UUID")

    return profile_id


async def get_profile_timezone(x_profile_timezone: str = Header(...)) -> str:
    if not x_profile_timezone:
        raise BadRequestError("Missing X-Profile-Timezone header")

    return x_profile_timezone


async def get_profile_context(
    profile_id: UUID = Depends(get_profile_id),
    timezone: str = Depends(get_profile_timezone),
    profile_repo: ProfileRepo = Depends(get_profile_repository),
) -> ProfileContext:

    profile = await profile_repo.fetch(profile_id)
    await profile_repo.update_timezone(profile.id, timezone)
    return ProfileContext(profile_id=profile_id, timezone=timezone)
