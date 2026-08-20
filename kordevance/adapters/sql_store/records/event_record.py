from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

from kordevance.domain.models.engine_source import EngineSource


class EventRecord(SQLModel, table=True):
    __tablename__ = "events"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    profile_id: UUID = Field(primary_key=True)
    goal_id: UUID | None = None

    engine_source: EngineSource

    connector_provider: str | None = None
    origin_signature: str | None = None

    raw_content: str
    occurred_at: datetime

    classified_type: str | None = None
    extracted_fields: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    confidence: float | None = None

    linked_task_id: UUID | None = None

    created_at: datetime
