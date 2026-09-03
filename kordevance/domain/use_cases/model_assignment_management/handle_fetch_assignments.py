import logging
from uuid import UUID

from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.models.model_assignment import ModelAssignment
from kordevance.domain.ports.model_assignment_repository import ModelAssignmentRepo


class HandleFetchModelAssignments(UseCase[UUID, list[ModelAssignment]]):
    def __init__(self, repository: ModelAssignmentRepo) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._repository: ModelAssignmentRepo = repository

    async def execute(self, profile_id: UUID) -> list[ModelAssignment]:
        self._logger.info(f"Fetching model assignments for profile {profile_id}")
        return await self._repository.fetch_all(profile_id)
