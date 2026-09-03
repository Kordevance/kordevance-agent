import logging
from uuid import UUID

from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.models.llm_provider import LLMProvider
from kordevance.domain.ports.llm_provider_repository import LLMProviderRepo


class HandleFetchProviders(UseCase[UUID, list[LLMProvider]]):
    def __init__(self, repository: LLMProviderRepo) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._repository: LLMProviderRepo = repository

    async def execute(self, profile_id: UUID) -> list[LLMProvider]:
        self._logger.info(f"Fetching LLM providers for profile {profile_id}")
        return await self._repository.fetch_all(profile_id)
