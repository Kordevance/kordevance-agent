import logging

from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.models.profile import Profile
from kordevance.domain.ports.profile_repository import ProfileRepo


class HandleCreateProfile(UseCase[str, Profile]):
    def __init__(self, profile_repository: ProfileRepo) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._repository: ProfileRepo = profile_repository

    async def execute(self, profile_name: str) -> Profile:
        self._logger.info(f"Handling profile creation for profile {profile_name}")
        profile = await self._repository.save(profile_name)

        self._logger.info(f"Profile {profile_name} created successfully")
        return profile
