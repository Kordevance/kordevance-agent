from uuid import UUID

from pydantic import BaseModel

from kordevance.domain.models.model_role import ModelRole


class ModelAssignment(BaseModel):
    role: ModelRole
    provider_id: UUID
    model_id: str
