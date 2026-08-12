from abc import ABC, abstractmethod
from uuid import UUID

from kordevance.domain.models.llm_provider import LLMProvider


class LLMProviderRepo(ABC):
    @abstractmethod
    async def save(self, profile_id: UUID, provider: LLMProvider) -> None: ...
    @abstractmethod
    async def delete(self, profile_id: UUID, provider_id: UUID) -> None: ...
    @abstractmethod
    async def fetch(self, profile_id: UUID, provider_id: UUID) -> LLMProvider: ...
    @abstractmethod
    async def fetch_all(self, profile_id: UUID) -> list[LLMProvider]: ...
