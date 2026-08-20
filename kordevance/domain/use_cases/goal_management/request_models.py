from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from kordevance.domain.models.connectors import Connector
from kordevance.domain.models.goal import HorizonGranularity, ProgressMetricType


class CreateGoalRequest(BaseModel):
    profile_id: UUID
    title: str
    description: str | None = None
    domain: str
    start_at: datetime
    end_at: datetime
    horizon_granularity: HorizonGranularity | None = None
    due_date: datetime | None = None
    progress_metric_type: ProgressMetricType
    target_value: float | None = None
    required_connectors: list[Connector] = []


class DeleteGoalRequest(BaseModel):
    profile_id: UUID
    goal_id: UUID
