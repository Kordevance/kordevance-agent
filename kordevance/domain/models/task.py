from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from kordevance.domain.models.engine_source import EngineSource


class TaskStatus(StrEnum):
    PENDING = "pending"
    USER_DONE = "user_done"
    INFERRED_DONE = "inferred_done"
    VERIFIED = "verified"
    CANCELLED = "cancelled"


class Task(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    goal_id: UUID
    profile_id: UUID
    title: str
    description: str | None = None

    due_date: datetime | None = None

    status: TaskStatus = TaskStatus.PENDING
    status_confidence: float | None = None

    source_type: EngineSource
    # The Event that produced or most recently updated this Task, if any.
    provenance_event_id: UUID | None = None

    external_actions: dict[str, str] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
