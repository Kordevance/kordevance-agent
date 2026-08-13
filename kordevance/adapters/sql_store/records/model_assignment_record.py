from uuid import UUID

from sqlmodel import Field, SQLModel

from kordevance.domain.models.model_role import ModelRole


class ModelAssignmentRecord(SQLModel, table=True):
    __tablename__ = "model_assignments"

    profile_id: UUID = Field(primary_key=True)
    role: ModelRole = Field(primary_key=True)
    provider_id: UUID
    model_id: str
