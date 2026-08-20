from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from kordevance.domain.models.connectors import Connector


class GoalStatus(StrEnum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class HorizonGranularity(StrEnum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


class ProgressMetricType(StrEnum):
    BOOLEAN = "boolean"
    NUMERIC = "numeric"
    MILESTONE_COUNT = "milestone_count"


class Goal(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    profile_id: UUID
    title: str
    description: str | None = None
    domain: str
    status: GoalStatus = GoalStatus.ACTIVE

    start_at: datetime
    end_at: datetime
    horizon_granularity: HorizonGranularity

    # Optional decision/action deadline, distinct from end_at. Use this when the user needs a
    # decision or output *by* a specific date that is earlier than the goal's own horizon end —
    # e.g. "find me flights, but tell me what you've got by November 12" for a trip that itself
    # runs through the end of December. When set, engines should treat it as the point by which
    # they must surface a result (or their best partial result) regardless of confidence, rather
    # than as the goal's actual end. Leave unset for goals where end_at already is the deadline.
    due_date: datetime | None = None

    progress_metric_type: ProgressMetricType
    target_value: float | None = None
    current_value: float = 0

    required_connectors: list[Connector] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
