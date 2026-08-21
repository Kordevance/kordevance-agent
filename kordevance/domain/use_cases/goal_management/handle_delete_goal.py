from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.ports.goal_repository import GoalRepo
from kordevance.domain.ports.job_scheduler import JobScheduler
from kordevance.domain.services.goal_service import GoalService
from kordevance.domain.use_cases.goal_management.request_models import DeleteGoalRequest


class HandleDeleteGoal(UseCase[DeleteGoalRequest, None]):
    def __init__(self, repository: GoalRepo, job_scheduler: JobScheduler) -> None:
        self._service: GoalService = GoalService(repository=repository)
        self._job_scheduler: JobScheduler = job_scheduler

    async def execute(self, request: DeleteGoalRequest) -> None:
        await self._service.delete_goal(request.profile_id, request.goal_id)
        self._job_scheduler.unschedule_goal_cycle(request.goal_id)
