import logging

from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.models.profile import Profile
from kordevance.domain.ports.profile_repository import ProfileRepo
from kordevance.domain.ports.profile_workspace import ProfileWorkspace
from kordevance.domain.use_cases.profile_management.request_models import CreateProfileRequest


class HandleCreateProfile(UseCase[CreateProfileRequest, Profile]):
    def __init__(self, profile_repository: ProfileRepo, workspace: ProfileWorkspace) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._repository: ProfileRepo = profile_repository
        self._workspace: ProfileWorkspace = workspace

    async def execute(self, request: CreateProfileRequest) -> Profile:
        self._logger.info(f"Handling profile creation for profile {request.name}")
        profile = await self._repository.save(request.name, request.timezone, request.timezone)

        try:
            await self._workspace.create_profile(profile.id)
        except OSError:
            self._logger.exception(
                f"Failed to create workspace for profile {profile.id}; rolling back profile creation"
            )
            await self._repository.delete(profile.id)
            raise

        self._logger.info(f"Profile {request.name} created successfully")
        return profile
