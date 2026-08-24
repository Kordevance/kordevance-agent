from uuid import UUID, uuid4

from fastapi import APIRouter, Depends

from kordevance.application.dependencies.auth import require_paired_device
from kordevance.application.dependencies.chat import ChatOrchestratorDep, FetchConversationsUseCaseDep
from kordevance.application.dependencies.deps import get_profile_id
from kordevance.application.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ConversationResponse,
    ConversationsResponse,
)
from kordevance.domain.use_cases.orchestration.request_models import ChatOrchestrationRequest

router: APIRouter = APIRouter(prefix="/chat", tags=["chat"], dependencies=[Depends(require_paired_device)])


@router.post("/message")
async def send_message(
    body: ChatMessageRequest, service: ChatOrchestratorDep, profile_id: UUID = Depends(get_profile_id)
) -> ChatMessageResponse:
    conversation_id = body.conversation_id or uuid4()
    request = ChatOrchestrationRequest(profile_id=profile_id, conversation_id=conversation_id, message=body.message)
    reply = await service.execute(request)
    return ChatMessageResponse(conversation_id=conversation_id, reply=reply)


@router.get("/conversations")
async def get_conversations(
    service: FetchConversationsUseCaseDep, profile_id: UUID = Depends(get_profile_id)
) -> ConversationsResponse:
    conversations = await service.execute(profile_id)
    return ConversationsResponse(
        conversations=[ConversationResponse(id=c.id, messages=c.messages, timestamp=c.timestamp) for c in conversations]
    )
