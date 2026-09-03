import logging

from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.models.llm_provider import LLMProvider
from kordevance.domain.ports.llm_provider_repository import LLMProviderRepo
from kordevance.domain.use_cases.llm_provider_management.request_models import GenericProviderRequest


class HandleFetchProvider(UseCase[GenericProviderRequest, LLMProvider]):
    def __init__(self, repository: LLMProviderRepo) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._repository: LLMProviderRepo = repository

    async def execute(self, request: GenericProviderRequest) -> LLMProvider:
        self._logger.info(f"Fetching LLM provider {request.profile_id}")
        return await self._repository.fetch(request.profile_id, request.provider_id)
