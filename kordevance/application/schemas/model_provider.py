from uuid import UUID

from pydantic import BaseModel


class ModelProviderRequest(BaseModel):
    name: str
    api_key: str
    endpoint: str | None = None


class ModelProviderResponse(BaseModel):
    id: UUID
    token_usage: int
