from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from kordevance.domain.models.connectors import ConnectorTypes


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

    progress_metric_type: ProgressMetricType
    target_value: float | None = None
    current_value: float = 0

    required_connectors: list[ConnectorTypes] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
