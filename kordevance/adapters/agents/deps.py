from dataclasses import dataclass
from uuid import UUID

from kordevance.domain.use_cases.goal_management.handle_create_goal import HandleCreateGoal


@dataclass
class GoalDefinitionDeps:
    profile_id: UUID
    create_goal_use_case: HandleCreateGoal
