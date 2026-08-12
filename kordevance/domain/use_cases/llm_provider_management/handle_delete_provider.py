import logging

from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.ports.llm_provider_repository import LLMProviderRepo
from kordevance.domain.use_cases.llm_provider_management.request_models import GenericProviderRequest


class HandleDeleteProvider(UseCase[GenericProviderRequest, None]):
    def __init__(self, repository: LLMProviderRepo) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._repository: LLMProviderRepo = repository

    async def execute(self, request: GenericProviderRequest) -> None:
        self._logger.info(f"Deleting LLM provider {request.profile_id}")
        await self._repository.delete(request.profile_id, request.provider_id)
