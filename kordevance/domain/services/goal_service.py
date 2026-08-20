import logging
from datetime import UTC, datetime
from uuid import UUID

from kordevance.domain.models.connectors import Connector
from kordevance.domain.models.goal import Goal, GoalStatus, HorizonGranularity, ProgressMetricType
from kordevance.domain.ports.goal_repository import GoalRepo
from kordevance.exceptions import BadRequestError


class GoalService:
    def __init__(self, repository: GoalRepo) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._repository: GoalRepo = repository

    async def create_goal(
        self,
        profile_id: UUID,
        title: str,
        domain: str,
        start_at: datetime,
        end_at: datetime,
        horizon_granularity: HorizonGranularity,
        progress_metric_type: ProgressMetricType,
        description: str | None = None,
        due_date: datetime | None = None,
        target_value: float | None = None,
        required_connectors: list[Connector] | None = None,
    ) -> Goal:
        self._logger.info(f"Creating goal '{title}' for profile {profile_id}")

        if progress_metric_type != ProgressMetricType.BOOLEAN and target_value is None:
            raise BadRequestError(f"target_value is required when progress_metric_type is '{progress_metric_type}'")

        if end_at <= start_at:
            raise BadRequestError("end_at must be after start_at")

        if due_date is not None and not (start_at <= due_date <= end_at):
            raise BadRequestError("due_date must fall between start_at and end_at")

        now = datetime.now(UTC)
        goal = Goal(
            profile_id=profile_id,
            title=title,
            description=description,
            domain=domain,
            status=GoalStatus.ACTIVE,
            start_at=start_at,
            end_at=end_at,
            horizon_granularity=horizon_granularity,
            due_date=due_date,
            progress_metric_type=progress_metric_type,
            target_value=target_value,
            current_value=0,
            required_connectors=required_connectors or [],
            created_at=now,
            updated_at=now,
        )

        await self._repository.save(goal)
        self._logger.info(f"Goal '{title}' created successfully with ID {goal.id}")
        return goal
