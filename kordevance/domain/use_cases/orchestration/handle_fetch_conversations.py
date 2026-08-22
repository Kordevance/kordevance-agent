from uuid import UUID

from kordevance.domain.contracts.use_case import UseCase
from kordevance.domain.models.conversation import Conversation
from kordevance.domain.ports.chat_orchestrator import ChatOrchestrator
from kordevance.domain.ports.message_store import MessageStore


class HandleFetchConversations(UseCase[UUID, list[Conversation]]):
    def __init__(self, message_store: MessageStore, chat_orchestrator: ChatOrchestrator) -> None:
        self._message_store: MessageStore = message_store
        self._chat_orchestrator: ChatOrchestrator = chat_orchestrator

    async def execute(self, request: UUID) -> list[Conversation]:
        conversation_ids = await self._message_store.list_conversations(request)
        conversations = []
        for conversation_id in conversation_ids:
            messages = await self._chat_orchestrator.get_history(request, conversation_id)
            conversations.append(Conversation(id=conversation_id, messages=messages))
        return conversations
