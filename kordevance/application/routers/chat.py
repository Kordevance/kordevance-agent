from uuid import UUID, uuid4

from fastapi import APIRouter, Depends

from kordevance.application.dependencies.chat import ChatOrchestratorDep
from kordevance.application.dependencies.deps import get_profile_id
from kordevance.application.schemas.chat import ChatMessageRequest, ChatMessageResponse

router: APIRouter = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/message")
async def send_message(
    body: ChatMessageRequest, service: ChatOrchestratorDep, profile_id: UUID = Depends(get_profile_id)
) -> ChatMessageResponse:
    conversation_id = body.conversation_id or uuid4()
    reply = await service.handle_message(profile_id, conversation_id, body.message)
    return ChatMessageResponse(conversation_id=conversation_id, reply=reply)
