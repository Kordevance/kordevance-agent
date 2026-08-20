from uuid import UUID

from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.models.goal import Goal
from kordevance.domain.ports.goal_repository import GoalRepo
from kordevance.domain.services.goal_service import GoalService


class HandleFetchGoals(UseCase[UUID, list[Goal]]):
    def __init__(self, repository: GoalRepo) -> None:
        self._service: GoalService = GoalService(repository=repository)

    async def execute(self, profile_id: UUID) -> list[Goal]:
        return await self._service.get_all_goals(profile_id)
