from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class GoalCycleCandidate(BaseModel):
    """A new option the engine found that satisfies the goal — e.g. a course, a flight."""

    title: str
    description: str
    # How well this candidate matches the goal's stated preferences/constraints (0-1).
    confidence: float = Field(ge=0, le=1)
    due_date: datetime | None = None


class TaskCompletionSignal(BaseModel):
    """Evidence that an existing task looks done. Always maps to INFERRED_DONE, never a stronger
    status (the engine classifies, it doesn't verify)
    """

    task_id: UUID
    confidence: float = Field(ge=0, le=1)
    reason: str


class GoalCycleFinding(BaseModel):
    candidates: list[GoalCycleCandidate] = Field(default_factory=list)
    completed_tasks: list[TaskCompletionSignal] = Field(default_factory=list)
    summary: str
