from pydantic import BaseModel


class GoalCycleTriageDecision(BaseModel):
    should_explore: bool
    reason: str
