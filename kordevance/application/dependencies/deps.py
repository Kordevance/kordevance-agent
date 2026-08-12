from uuid import UUID

from fastapi import Header

from kordevance.application.utils import parse_id
from kordevance.exceptions import BadRequestError


async def get_profile_id(x_profile_id: str = Header(...)) -> UUID:
    if not x_profile_id:
        raise BadRequestError("Missing X-Profile-Id header")

    profile_id = parse_id(x_profile_id)
    if profile_id is None:
        raise BadRequestError("X-Profile-Id must be a valid UUID")

    return profile_id
