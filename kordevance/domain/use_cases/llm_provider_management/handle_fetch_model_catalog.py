import logging

from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.models.llm_provider import AuthorizedLLMProviders
from kordevance.domain.ports.llm_provider_repository import LLMProviderRepo
from kordevance.domain.ports.model_catalog_client import ModelCatalogClient
from kordevance.domain.use_cases.llm_provider_management.request_models import GenericProviderRequest


class HandleFetchModelCatalog(UseCase[GenericProviderRequest, list[str]]):
    def __init__(self, repository: LLMProviderRepo, catalog_client: ModelCatalogClient) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._repository: LLMProviderRepo = repository
        self._catalog_client: ModelCatalogClient = catalog_client

    async def execute(self, request: GenericProviderRequest) -> list[str]:
        self._logger.info(f"Fetching model catalog for provider {request.provider_id}")

        provider = await self._repository.fetch(request.profile_id, request.provider_id)
        if provider.name == AuthorizedLLMProviders.Other:
            return []

        return await self._catalog_client.list_models(
            provider=provider.name, endpoint=provider.endpoint, api_key=provider.api_key
        )
