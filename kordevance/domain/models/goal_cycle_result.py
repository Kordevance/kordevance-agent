from uuid import UUID

from pydantic import BaseModel, Field


class GoalCycleResult(BaseModel):
    goal_id: UUID
    tasks_created: list[UUID] = Field(default_factory=list)
    tasks_updated: list[UUID] = Field(default_factory=list)
    events_created: list[UUID] = Field(default_factory=list)

    # Tasks whose due_date is imminent and aren't yet in a terminal status
    tasks_needing_final_reminder: list[UUID] = Field(default_factory=list)

    notes: list[str] = Field(default_factory=list)
