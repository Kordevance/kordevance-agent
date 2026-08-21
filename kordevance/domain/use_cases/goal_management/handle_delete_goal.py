from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.ports.event_repository import EventRepo
from kordevance.domain.ports.goal_repository import GoalRepo
from kordevance.domain.ports.job_scheduler import JobScheduler
from kordevance.domain.ports.task_repository import TaskRepo
from kordevance.domain.services.goal_service import GoalService
from kordevance.domain.use_cases.goal_management.request_models import DeleteGoalRequest


class HandleDeleteGoal(UseCase[DeleteGoalRequest, None]):
    def __init__(
        self,
        repository: GoalRepo,
        task_repo: TaskRepo,
        event_repo: EventRepo,
        job_scheduler: JobScheduler,
    ) -> None:
        self._service: GoalService = GoalService(repository=repository)
        self._task_repo: TaskRepo = task_repo
        self._event_repo: EventRepo = event_repo
        self._job_scheduler: JobScheduler = job_scheduler

    async def execute(self, request: DeleteGoalRequest) -> None:
        await self._service.delete_goal(request.profile_id, request.goal_id)
        await self._task_repo.delete_all_for_goal(request.profile_id, request.goal_id)
        await self._event_repo.delete_all_for_goal(request.profile_id, request.goal_id)
        self._job_scheduler.unschedule_goal_cycle(request.goal_id)
