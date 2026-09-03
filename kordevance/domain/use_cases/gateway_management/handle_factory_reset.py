from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.ports.event_repository import EventRepo
from kordevance.domain.ports.goal_repository import GoalRepo
from kordevance.domain.ports.llm_provider_repository import LLMProviderRepo
from kordevance.domain.ports.model_assignment_repository import ModelAssignmentRepo
from kordevance.domain.ports.profile_repository import ProfileRepo
from kordevance.domain.ports.profile_workspace import ProfileWorkspace
from kordevance.domain.ports.task_repository import TaskRepo
from kordevance.domain.services.pairing_service import PairingService


class HandleFactoryReset(UseCase[None, str | None]):
    def __init__(
        self,
        pairing_service: PairingService,
        profile_repo: ProfileRepo,
        llm_provider_repo: LLMProviderRepo,
        model_assignment_repo: ModelAssignmentRepo,
        goal_repo: GoalRepo,
        task_repo: TaskRepo,
        event_repo: EventRepo,
        profile_workspace: ProfileWorkspace,
    ) -> None:
        self._pairing_service: PairingService = pairing_service
        self._profile_repo: ProfileRepo = profile_repo
        self._llm_provider_repo: LLMProviderRepo = llm_provider_repo
        self._model_assignment_repo: ModelAssignmentRepo = model_assignment_repo
        self._goal_repo: GoalRepo = goal_repo
        self._task_repo: TaskRepo = task_repo
        self._event_repo: EventRepo = event_repo
        self._profile_workspace: ProfileWorkspace = profile_workspace

    async def execute(self, request: None = None) -> str | None:
        await self._event_repo.delete_all()
        await self._task_repo.delete_all()
        await self._goal_repo.delete_all()
        await self._model_assignment_repo.delete_all()
        await self._llm_provider_repo.delete_all()
        await self._profile_repo.delete_all()
        await self._profile_workspace.delete_all()

        return await self._pairing_service.repair()
