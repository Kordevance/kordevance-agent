import logging

from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.models.goal import Goal
from kordevance.domain.ports.goal_repository import GoalRepo
from kordevance.domain.services.goal_service import GoalService
from kordevance.domain.use_cases.goal_management.request_models import CreateGoalRequest


class HandleCreateGoal(UseCase[CreateGoalRequest, Goal]):
    def __init__(self, repository: GoalRepo) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._service: GoalService = GoalService(repository=repository)

    async def execute(self, request: CreateGoalRequest) -> Goal:
        return await self._service.create_goal(
            profile_id=request.profile_id,
            title=request.title,
            description=request.description,
            domain=request.domain,
            start_at=request.start_at,
            end_at=request.end_at,
            horizon_granularity=request.horizon_granularity,
            due_date=request.due_date,
            progress_metric_type=request.progress_metric_type,
            target_value=request.target_value,
            required_connectors=request.required_connectors,
        )
