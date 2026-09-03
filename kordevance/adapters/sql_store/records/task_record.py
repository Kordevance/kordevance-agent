from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

from kordevance.domain.models.engine_source import EngineSource
from kordevance.domain.models.task import TaskStatus


class TaskRecord(SQLModel, table=True):
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    profile_id: UUID = Field(primary_key=True)
    goal_id: UUID
    title: str
    description: str | None = None
    due_date: datetime | None = None

    status: TaskStatus
    status_confidence: float | None = None

    source_type: EngineSource
    provenance_event_id: UUID | None = None

    external_actions: dict[str, str] = Field(default_factory=dict, sa_column=Column(JSON))

    created_at: datetime
    updated_at: datetime
