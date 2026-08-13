import logging
from datetime import UTC, datetime

from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.models.goal import Goal, GoalStatus, ProgressMetricType
from kordevance.domain.ports.goal_repository import GoalRepo
from kordevance.domain.use_cases.goal_management.request_models import CreateGoalRequest
from kordevance.exceptions import BadRequestError


class HandleCreateGoal(UseCase[CreateGoalRequest, Goal]):
    def __init__(self, repository: GoalRepo) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._repository: GoalRepo = repository

    async def execute(self, request: CreateGoalRequest) -> Goal:
        self._logger.info(f"Creating goal '{request.title}' for profile {request.profile_id}")

        if request.progress_metric_type != ProgressMetricType.BOOLEAN and request.target_value is None:
            raise BadRequestError(
                f"target_value is required when progress_metric_type is '{request.progress_metric_type}'"
            )

        if request.end_at <= request.start_at:
            raise BadRequestError("end_at must be after start_at")

        now = datetime.now(UTC)
        goal = Goal(
            profile_id=request.profile_id,
            title=request.title,
            description=request.description,
            domain=request.domain,
            status=GoalStatus.ACTIVE,
            start_at=request.start_at,
            end_at=request.end_at,
            horizon_granularity=request.horizon_granularity,
            progress_metric_type=request.progress_metric_type,
            target_value=request.target_value,
            current_value=0,
            required_connectors=request.required_connectors,
            created_at=now,
            updated_at=now,
        )

        await self._repository.save(goal)
        self._logger.info(f"Goal '{request.title}' created successfully with ID {goal.id}")
        return goal
