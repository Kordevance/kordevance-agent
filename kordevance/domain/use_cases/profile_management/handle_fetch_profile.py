import logging
from uuid import UUID

from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.models.profile import Profile
from kordevance.domain.ports.profile_repository import ProfileRepo


class HandleFetchProfile(UseCase[UUID, Profile]):
    def __init__(self, profile_repository: ProfileRepo) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._repository: ProfileRepo = profile_repository

    async def execute(self, profile_id: UUID) -> Profile:
        self._logger.info(f"Handling profile retrieval for profile {profile_id}")
        return await self._repository.fetch(profile_id)
