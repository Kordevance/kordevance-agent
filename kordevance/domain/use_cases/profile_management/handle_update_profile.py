import logging

from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.models.profile import Profile
from kordevance.domain.ports.profile_repository import ProfileRepo


class HandleUpdateProfile(UseCase[Profile, None]):
    def __init__(self, profile_repository: ProfileRepo) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._repository: ProfileRepo = profile_repository

    async def execute(self, request: Profile) -> None:
        self._logger.info(f"Handling profile update for profile {request.id}")
        return await self._repository.update(request)
