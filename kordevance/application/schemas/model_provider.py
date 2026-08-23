from uuid import UUID

from pydantic import BaseModel

from kordevance.domain.models.llm_provider import AuthorizedLLMProviders, LLMProvider


class ModelProviderRequest(BaseModel):
    name: str
    api_key: str
    endpoint: str | None = None
    display_name: str | None = None


class ModelProviderResponse(BaseModel):
    id: UUID
    name: str

    @classmethod
    def from_domain(cls, provider: LLMProvider) -> "ModelProviderResponse":
        name = (
            provider.display_name or provider.name.value
            if provider.name == AuthorizedLLMProviders.Other
            else provider.name.value
        )
        return cls(id=provider.id, name=name)
