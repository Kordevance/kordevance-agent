import logging

from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.models.model_role import ModelRole
from kordevance.domain.ports.model_assignment_repository import ModelAssignmentRepo
from kordevance.domain.use_cases.model_assignment_management.request_models import DeleteModelAssignmentRequest
from kordevance.exceptions import BadRequestError


class HandleDeleteModelAssignment(UseCase[DeleteModelAssignmentRequest, None]):
    def __init__(self, repository: ModelAssignmentRepo) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._repository: ModelAssignmentRepo = repository

    async def execute(self, request: DeleteModelAssignmentRequest) -> None:
        self._logger.info(f"Deleting {request.role} model assignment for profile {request.profile_id}")

        if request.role == ModelRole.PRIMARY:
            raise BadRequestError("The primary model assignment cannot be removed; reassign it to another model")

        await self._repository.delete(request.profile_id, request.role)
