from uuid import UUID

from pydantic import BaseModel

from kordevance.domain.models.model_role import ModelRole


class SetModelAssignmentRequest(BaseModel):
    profile_id: UUID
    role: ModelRole
    provider_id: UUID
    model_id: str


class DeleteModelAssignmentRequest(BaseModel):
    profile_id: UUID
    role: ModelRole
