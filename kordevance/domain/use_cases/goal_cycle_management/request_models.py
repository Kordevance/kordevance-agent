from uuid import UUID

from pydantic import BaseModel


class RunGoalCycleRequest(BaseModel):
    profile_id: UUID
    goal_id: UUID
