from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.ports.chat_orchestrator import ChatOrchestrator
from kordevance.domain.use_cases.orchestration.request_models import ChatOrchestrationRequest


class HandleChatOrchestration(UseCase[ChatOrchestrationRequest, str]):
    def __init__(self, chat_orchestrator: ChatOrchestrator) -> None:
        self._orchestrator: ChatOrchestrator = chat_orchestrator

    async def execute(self, request: ChatOrchestrationRequest) -> str:
        return await self._orchestrator.handle_message(
            request.profile_id, request.conversation_id, request.message, request.timezone
        )
