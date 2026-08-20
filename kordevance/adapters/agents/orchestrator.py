from datetime import UTC, datetime
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
from kordevance.domain.ports.message_store import MessageStore
from kordevance.domain.use_cases.connectors_management.handle_fetch_connectors import HandleFetchConnectors
from kordevance.domain.use_cases.goal_management.handle_create_goal import HandleCreateGoal

_ORCHESTRATOR_INSTRUCTIONS = (
    AGENT_PERSONA
    + """
You are the routing layer for Kordevance, a personal planning assistant. You never discuss plans
or goals in detail yourself — you only decide, for each incoming message, whether it expresses
wanting something achieved, tracked, or watched for over time (a new goal — this includes ongoing
requests like "keep an eye on my mail for X and do Y", not just fixed targets), in which case you
hand off to the goal-definition specialist. For anything else, reply briefly and helpfully
yourself.
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
        create_goal_use_case: HandleCreateGoal,
        fetch_connectors_use_case: HandleFetchConnectors,
    ) -> None:
        self._model_resolver: ModelResolver = model_resolver
        self._message_store: MessageStore = message_store
        self._create_goal_use_case: HandleCreateGoal = create_goal_use_case
        self._fetch_connectors_use_case: HandleFetchConnectors = fetch_connectors_use_case

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
        now = datetime.now(UTC)

        triage_model = await self._model_resolver.resolve(profile_id, ModelRole.TRIAGE)
        orchestrator: Agent[None, GoalDefinitionHandoff | str] = Agent(
            model=triage_model,
            output_type=[GoalDefinitionHandoff, str],
            instructions=_ORCHESTRATOR_INSTRUCTIONS + f"\n\nCurrent date and time: {now.isoformat()}",
        )
        route_result = await orchestrator.run(message, message_history=history)

        if isinstance(route_result.output, GoalDefinitionHandoff):
            primary_model = await self._model_resolver.resolve(profile_id, ModelRole.PRIMARY)
            goal_agent = build_goal_definition_agent(primary_model, now)
            goal_deps = GoalDefinitionDeps(
                profile_id=profile_id,
                create_goal_use_case=self._create_goal_use_case,
                fetch_connectors_use_case=self._fetch_connectors_use_case,
            )
            goal_result = await goal_agent.run(message, message_history=history, deps=goal_deps)

            await self._persist_turn(profile_id, conversation_id, goal_result.new_messages())
            return goal_result.output

        await self._persist_turn(profile_id, conversation_id, route_result.new_messages())
        return route_result.output
