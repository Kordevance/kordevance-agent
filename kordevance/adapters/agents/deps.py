from dataclasses import dataclass
from uuid import UUID

from kordevance.domain.use_cases.connectors_management.handle_fetch_connectors import HandleFetchConnectors
from kordevance.domain.use_cases.goal_management.handle_create_goal import HandleCreateGoal


@dataclass
class GoalDefinitionDeps:
    profile_id: UUID
    create_goal_use_case: HandleCreateGoal
    fetch_connectors_use_case: HandleFetchConnectors
