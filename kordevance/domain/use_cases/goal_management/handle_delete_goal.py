from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.ports.goal_repository import GoalRepo
from kordevance.domain.services.goal_service import GoalService
from kordevance.domain.use_cases.goal_management.request_models import DeleteGoalRequest


class HandleDeleteGoal(UseCase[DeleteGoalRequest, None]):
    def __init__(self, repository: GoalRepo) -> None:
        self._service: GoalService = GoalService(repository=repository)

    async def execute(self, request: DeleteGoalRequest) -> None:
        return await self._service.delete_goal(request.profile_id, request.goal_id)
