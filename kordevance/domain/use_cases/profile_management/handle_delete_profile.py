import logging
from uuid import UUID

from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.ports.profile_repository import ProfileRepo
from kordevance.domain.ports.profile_workspace import ProfileWorkspace


class HandleDeleteProfile(UseCase[UUID, None]):
    def __init__(self, profile_repository: ProfileRepo, workspace: ProfileWorkspace) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._repository: ProfileRepo = profile_repository
        self._workspace: ProfileWorkspace = workspace

    async def execute(self, profile_id: UUID) -> None:
        self._logger.info(f"Handling profile deletion for profile {profile_id}")
        await self._repository.delete(profile_id)

        try:
            await self._workspace.delete_profile(profile_id)
        except OSError:
            # The DB row is already gone, which is what matters for correctness; a leftover
            # directory is a harmless disk leak, not a data-integrity problem, so we log and move on.
            self._logger.exception(f"Failed to delete workspace for profile {profile_id}; leaving it orphaned")
