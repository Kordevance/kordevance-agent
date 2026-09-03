import logging

from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.models.profile import Profile
from kordevance.domain.ports.profile_repository import ProfileRepo


class HandleFetchProfiles(UseCase[None, list[Profile]]):
    def __init__(self, profile_repository: ProfileRepo) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._repository: ProfileRepo = profile_repository

    async def execute(self, request: None = None) -> list[Profile]:
        self._logger.info("Fetching all profiles")
        return await self._repository.fetch_all()
