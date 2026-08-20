from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.models.goal import Goal
from kordevance.domain.ports.goal_repository import GoalRepo
from kordevance.domain.ports.job_scheduler import DEFAULT_CYCLE_INTERVAL_SECONDS, JobScheduler
from kordevance.domain.services.goal_service import GoalService
from kordevance.domain.use_cases.goal_management.request_models import CreateGoalRequest


class HandleCreateGoal(UseCase[CreateGoalRequest, Goal]):
    def __init__(self, repository: GoalRepo, job_scheduler: JobScheduler) -> None:
        self._service: GoalService = GoalService(repository=repository)
        self._job_scheduler: JobScheduler = job_scheduler

    async def execute(self, request: CreateGoalRequest) -> Goal:
        goal = await self._service.create_goal(
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

        # Keeps the goal's cron alive from the moment it exists
        self._job_scheduler.schedule_goal_cycle(
            profile_id=goal.profile_id, goal_id=goal.id, interval_seconds=DEFAULT_CYCLE_INTERVAL_SECONDS
        )

        return goal
