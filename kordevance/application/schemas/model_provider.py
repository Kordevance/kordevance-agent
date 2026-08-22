from uuid import UUID

from pydantic import BaseModel

from kordevance.domain.models.llm_provider import AuthorizedLLMProviders


class ModelProviderRequest(BaseModel):
    name: str
    api_key: str
    endpoint: str | None = None


class ModelProviderResponse(BaseModel):
    id: UUID
    name: AuthorizedLLMProviders
