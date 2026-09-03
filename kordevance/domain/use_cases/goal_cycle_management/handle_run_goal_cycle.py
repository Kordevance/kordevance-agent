from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.models.goal_cycle_result import GoalCycleResult
from kordevance.domain.ports.event_repository import EventRepo
from kordevance.domain.ports.goal_cycle_engine import GoalCycleEngine
from kordevance.domain.ports.goal_repository import GoalRepo
from kordevance.domain.ports.profile_repository import ProfileRepo
from kordevance.domain.ports.task_repository import TaskRepo
from kordevance.domain.services.goal_cycle_service import GoalCycleService
from kordevance.domain.use_cases.goal_cycle_management.request_models import RunGoalCycleRequest


class HandleRunGoalCycle(UseCase[RunGoalCycleRequest, GoalCycleResult]):
    """The single entry point a cron tick calls: run one cycle for one goal. Everything about
    what happens during the cycle is decided from the goal's own state."""

    def __init__(
        self,
        goal_repo: GoalRepo,
        task_repo: TaskRepo,
        event_repo: EventRepo,
        goal_cycle_engine: GoalCycleEngine,
        profile_repo: ProfileRepo,
    ) -> None:
        self._service: GoalCycleService = GoalCycleService(
            goal_repo=goal_repo,
            task_repo=task_repo,
            event_repo=event_repo,
            goal_cycle_engine=goal_cycle_engine,
            profile_repo=profile_repo,
        )

    async def execute(self, request: RunGoalCycleRequest) -> GoalCycleResult:
        return await self._service.run_cycle(request.profile_id, request.goal_id)
