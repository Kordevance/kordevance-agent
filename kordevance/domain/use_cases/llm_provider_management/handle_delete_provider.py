import logging

from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.ports.llm_provider_repository import LLMProviderRepo
from kordevance.domain.ports.model_assignment_repository import ModelAssignmentRepo
from kordevance.domain.use_cases.llm_provider_management.request_models import GenericProviderRequest


class HandleDeleteProvider(UseCase[GenericProviderRequest, None]):
    def __init__(self, repository: LLMProviderRepo, model_assignment_repository: ModelAssignmentRepo) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._repository: LLMProviderRepo = repository
        self._model_assignment_repository: ModelAssignmentRepo = model_assignment_repository

    async def execute(self, request: GenericProviderRequest) -> None:
        self._logger.info(f"Deleting LLM provider {request.profile_id}")
        await self._repository.delete(request.profile_id, request.provider_id)

        assignments = await self._model_assignment_repository.fetch_all(request.profile_id)
        for assignment in assignments:
            if assignment.provider_id == request.provider_id:
                await self._model_assignment_repository.delete(request.profile_id, assignment.role)
