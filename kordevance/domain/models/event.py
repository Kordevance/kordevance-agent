from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from kordevance.domain.models.engine_source import EngineSource


class Event(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    profile_id: UUID
    goal_id: UUID | None = None

    engine_source: EngineSource

    connector_provider: str | None = None
    origin_signature: str | None = None

    raw_content: str
    occurred_at: datetime

    classified_type: str | None = None
    extracted_fields: dict[str, Any] = Field(default_factory=dict)
    # Classification/extraction confidence (0-1).
    confidence: float | None = None

    linked_task_id: UUID | None = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
