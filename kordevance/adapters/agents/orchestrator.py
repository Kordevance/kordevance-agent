from uuid import UUID

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage, ModelMessagesTypeAdapter

from kordevance.adapters.agents.deps import GoalDefinitionDeps
from kordevance.adapters.agents.goal_definition_agent import build_goal_definition_agent
from kordevance.adapters.agents.model_resolver import ModelResolver
from kordevance.adapters.agents.persona import AGENT_PERSONA
from kordevance.domain.models.model_role import ModelRole
from kordevance.domain.ports.chat_orchestrator import ChatOrchestrator
from kordevance.domain.ports.goal_repository import GoalRepo
from kordevance.domain.ports.message_store import MessageStore
from kordevance.domain.ports.oauth_connection_repository import OAuthConnectionRepo
from kordevance.domain.ports.profile_connector_assignment_repository import ProfileConnectorAssignmentRepo
from kordevance.domain.use_cases.connector_management.handle_fetch_connector_status import (
    HandleFetchConnectorStatus,
)
from kordevance.domain.use_cases.goal_management.handle_create_goal import HandleCreateGoal

_ORCHESTRATOR_INSTRUCTIONS = (
    AGENT_PERSONA
    + """
You are the routing layer for Kordevance, a personal planning assistant. You never discuss plans
or goals in detail yourself — you only decide, for each incoming message, whether it expresses
wanting to achieve/start/finish something (a new goal), in which case you hand off to the
goal-definition specialist. For anything else, reply briefly and helpfully yourself.
"""
)


class GoalDefinitionHandoff(BaseModel):
    """Route this message to the goal-definition specialist."""

    reason: str


class PydanticAIChatOrchestrator(ChatOrchestrator):
    """ChatOrchestrator implementation built on pydantic-ai"""

    def __init__(
        self,
        model_resolver: ModelResolver,
        message_store: MessageStore,
        goal_repo: GoalRepo,
        connector_assignment_repo: ProfileConnectorAssignmentRepo,
        oauth_connection_repo: OAuthConnectionRepo,
    ) -> None:
        self._model_resolver: ModelResolver = model_resolver
        self._message_store: MessageStore = message_store
        self._goal_repo: GoalRepo = goal_repo
        self._connector_assignment_repo: ProfileConnectorAssignmentRepo = connector_assignment_repo
        self._oauth_connection_repo: OAuthConnectionRepo = oauth_connection_repo

    async def _load_history(self, profile_id: UUID, conversation_id: UUID) -> list[ModelMessage]:
        lines = await self._message_store.load_history(profile_id, conversation_id)
        messages: list[ModelMessage] = []
        for line in lines:
            messages.extend(ModelMessagesTypeAdapter.validate_json(line))
        return messages

    async def _persist_turn(self, profile_id: UUID, conversation_id: UUID, new_messages: list[ModelMessage]) -> None:
        if not new_messages:
            return
        payload = ModelMessagesTypeAdapter.dump_json(new_messages).decode("utf-8")
        await self._message_store.append(profile_id, conversation_id, payload)

    async def handle_message(self, profile_id: UUID, conversation_id: UUID, message: str) -> str:
        history = await self._load_history(profile_id, conversation_id)

        triage_model = await self._model_resolver.resolve(profile_id, ModelRole.TRIAGE)
        orchestrator: Agent[None, GoalDefinitionHandoff | str] = Agent(
            model=triage_model,
            output_type=[GoalDefinitionHandoff, str],
            instructions=_ORCHESTRATOR_INSTRUCTIONS,
        )
        route_result = await orchestrator.run(message, message_history=history)

        if isinstance(route_result.output, GoalDefinitionHandoff):
            primary_model = await self._model_resolver.resolve(profile_id, ModelRole.PRIMARY)
            goal_agent = build_goal_definition_agent(primary_model)
            goal_deps = GoalDefinitionDeps(
                profile_id=profile_id,
                create_goal_use_case=HandleCreateGoal(repository=self._goal_repo),
                fetch_connector_status_use_case=HandleFetchConnectorStatus(
                    assignment_repo=self._connector_assignment_repo, connection_repo=self._oauth_connection_repo
                ),
            )
            goal_result = await goal_agent.run(message, message_history=history, deps=goal_deps)

            await self._persist_turn(profile_id, conversation_id, goal_result.new_messages())
            return goal_result.output

        await self._persist_turn(profile_id, conversation_id, route_result.new_messages())
        return route_result.output
