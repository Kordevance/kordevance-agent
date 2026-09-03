from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from kordevance.domain.use_cases.connectors_management.handle_fetch_connectors import HandleFetchConnectors
from kordevance.domain.use_cases.goal_management.handle_create_goal import HandleCreateGoal


class HasConnectorLookup(Protocol):
    """Structural type for any deps that can look up the user's connectors."""

    profile_id: UUID
    fetch_connectors_use_case: HandleFetchConnectors


@dataclass
class GoalDefinitionDeps:
    profile_id: UUID
    create_goal_use_case: HandleCreateGoal
    fetch_connectors_use_case: HandleFetchConnectors


@dataclass
class OrchestratorDeps:
    profile_id: UUID
    fetch_connectors_use_case: HandleFetchConnectors
