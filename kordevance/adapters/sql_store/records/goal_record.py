from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

from kordevance.domain.models.connectors import Connector
from kordevance.domain.models.goal import GoalStatus, HorizonGranularity, ProgressMetricType


class GoalRecord(SQLModel, table=True):
    __tablename__ = "goals"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    profile_id: UUID = Field(primary_key=True)
    title: str
    description: str | None = None
    domain: str
    status: GoalStatus

    start_at: datetime
    end_at: datetime
    horizon_granularity: HorizonGranularity

    # optional decision/action deadline, distinct from end_at.
    due_date: datetime | None = None

    progress_metric_type: ProgressMetricType
    target_value: float | None = None
    current_value: float

    required_connectors: list[Connector] = Field(default_factory=list, sa_column=Column(JSON))

    created_at: datetime
    updated_at: datetime
