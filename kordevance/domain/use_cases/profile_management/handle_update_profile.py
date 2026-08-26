import logging

from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.ports.profile_repository import ProfileRepo
from kordevance.domain.use_cases.profile_management.request_models import UpdateProfileRequest


class HandleUpdateProfile(UseCase[UpdateProfileRequest, None]):
    def __init__(self, profile_repository: ProfileRepo) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._repository: ProfileRepo = profile_repository

    async def execute(self, request: UpdateProfileRequest) -> None:
        self._logger.info(f"Handling profile update for profile {request.profile_id}")
        profile = await self._repository.fetch(request.profile_id)
        profile.name = request.name
        profile.home_timezone = request.home_timezone
        await self._repository.update(profile)
