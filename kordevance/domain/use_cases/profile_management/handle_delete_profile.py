import logging
from uuid import UUID

from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.ports.goal_repository import GoalRepo
from kordevance.domain.ports.llm_provider_repository import LLMProviderRepo
from kordevance.domain.ports.model_assignment_repository import ModelAssignmentRepo
from kordevance.domain.ports.profile_repository import ProfileRepo
from kordevance.domain.ports.profile_workspace import ProfileWorkspace
from kordevance.domain.use_cases.goal_management.handle_delete_goal import HandleDeleteGoal
from kordevance.domain.use_cases.goal_management.request_models import DeleteGoalRequest


class HandleDeleteProfile(UseCase[UUID, None]):
    def __init__(
        self,
        profile_repository: ProfileRepo,
        workspace: ProfileWorkspace,
        goal_repository: GoalRepo,
        delete_goal_use_case: HandleDeleteGoal,
        llm_provider_repository: LLMProviderRepo,
        model_assignment_repository: ModelAssignmentRepo,
    ) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._repository: ProfileRepo = profile_repository
        self._workspace: ProfileWorkspace = workspace
        self._goal_repository: GoalRepo = goal_repository
        self._delete_goal_use_case: HandleDeleteGoal = delete_goal_use_case
        self._llm_provider_repository: LLMProviderRepo = llm_provider_repository
        self._model_assignment_repository: ModelAssignmentRepo = model_assignment_repository

    async def execute(self, profile_id: UUID) -> None:
        self._logger.info(f"Handling profile deletion for profile {profile_id}")

        goals = await self._goal_repository.fetch_all(profile_id)
        for goal in goals:
            await self._delete_goal_use_case.execute(DeleteGoalRequest(profile_id=profile_id, goal_id=goal.id))

        providers = await self._llm_provider_repository.fetch_all(profile_id)
        for provider in providers:
            await self._llm_provider_repository.delete(profile_id, provider.id)

        assignments = await self._model_assignment_repository.fetch_all(profile_id)
        for assignment in assignments:
            await self._model_assignment_repository.delete(profile_id, assignment.role)

        await self._repository.delete(profile_id)

        try:
            await self._workspace.delete_profile(profile_id)
        except OSError:
            self._logger.exception(f"Failed to delete workspace for profile {profile_id}; leaving it orphaned")
