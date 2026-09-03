from uuid import UUID

from pydantic import BaseModel


class AddProviderRequest(BaseModel):
    profile_id: UUID
    name: str
    api_key: str
    endpoint: str | None = None
    display_name: str | None = None


class GenericProviderRequest(BaseModel):
    profile_id: UUID
    provider_id: UUID
