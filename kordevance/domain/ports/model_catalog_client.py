from abc import ABC, abstractmethod

from kordevance.domain.models.llm_provider import AuthorizedLLMProviders


class ModelCatalogClient(ABC):
    @abstractmethod
    async def list_models(self, provider: AuthorizedLLMProviders, endpoint: str, api_key: str) -> list[str]:
        """Return the sub-model ids a provider currently exposes, fetched live from its API."""
        ...
