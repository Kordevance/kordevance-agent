from abc import ABC, abstractmethod
from uuid import UUID

from kordevance.domain.models.goal import Goal
from kordevance.domain.models.goal_cycle_finding import GoalCycleFinding
from kordevance.domain.models.task import Task


class GoalCycleEngine(ABC):
    @abstractmethod
    async def run(
        self,
        goal: Goal,
        profile_id: UUID,
        existing_tasks: list[Task],
        is_final_attempt: bool,
    ) -> GoalCycleFinding: ...
