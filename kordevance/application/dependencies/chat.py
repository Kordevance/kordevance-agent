from typing import Annotated

from fastapi import Depends

from kordevance.adapters.agents.model_resolver import ModelResolver
from kordevance.adapters.agents.orchestrator import PydanticAIChatOrchestrator
from kordevance.application.dependencies.fs_adapter import MessageStoreDep
from kordevance.application.dependencies.sql_store_adapter import GoalRepoDep, ModelAssignmentDep, ModelProviderDep
from kordevance.domain.ports.chat_orchestrator import ChatOrchestrator


def get_chat_orchestrator(
    model_assignment_repo: ModelAssignmentDep,
    llm_provider_repo: ModelProviderDep,
    message_store: MessageStoreDep,
    goal_repo: GoalRepoDep,
) -> ChatOrchestrator:
    model_resolver = ModelResolver(model_assignment_repo=model_assignment_repo, llm_provider_repo=llm_provider_repo)
    return PydanticAIChatOrchestrator(model_resolver=model_resolver, message_store=message_store, goal_repo=goal_repo)


ChatOrchestratorDep = Annotated[ChatOrchestrator, Depends(get_chat_orchestrator)]
