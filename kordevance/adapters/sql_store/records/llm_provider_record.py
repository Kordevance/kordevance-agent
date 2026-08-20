from uuid import UUID

from sqlmodel import Field, SQLModel

from kordevance.domain.models.llm_provider import AuthorizedLLMProviders


class LLMProviderRecord(SQLModel, table=True):
    __tablename__ = "llm_providers"

    id: UUID = Field(primary_key=True)
    profile_id: UUID = Field(primary_key=True)
    name: AuthorizedLLMProviders
    endpoint: str
    api_key_encrypted: str
