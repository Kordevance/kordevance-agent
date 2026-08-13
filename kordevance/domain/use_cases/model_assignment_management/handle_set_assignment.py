import logging

from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.models.model_assignment import ModelAssignment
from kordevance.domain.ports.llm_provider_repository import LLMProviderRepo
from kordevance.domain.ports.model_assignment_repository import ModelAssignmentRepo
from kordevance.domain.use_cases.model_assignment_management.request_models import SetModelAssignmentRequest


class HandleSetModelAssignment(UseCase[SetModelAssignmentRequest, ModelAssignment]):
    def __init__(self, repository: ModelAssignmentRepo, provider_repository: LLMProviderRepo) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._repository: ModelAssignmentRepo = repository
        self._provider_repository: LLMProviderRepo = provider_repository

    async def execute(self, request: SetModelAssignmentRequest) -> ModelAssignment:
        self._logger.info(f"Setting {request.role} model assignment for profile {request.profile_id}")

        # Raises ProviderNotFoundError if the provider doesn't belong to this profile.
        await self._provider_repository.fetch(request.profile_id, request.provider_id)

        assignment = ModelAssignment(role=request.role, provider_id=request.provider_id, model_id=request.model_id)
        await self._repository.save(request.profile_id, assignment)
        return assignment
