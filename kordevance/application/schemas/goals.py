from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from kordevance.domain.models.goal import GoalStatus


class GoalResponse(BaseModel):
    id: UUID
    title: str
    description: str | None
    start_at: datetime
    end_at: datetime
    status: GoalStatus
