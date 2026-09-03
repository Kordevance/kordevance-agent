from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.messages import (
    ModelMessage,
    ModelMessagesTypeAdapter,
    ModelRequest,
    ModelResponse,
    TextPart,
    UserPromptPart,
)
from pydantic_ai.tools import Tool

from kordevance.adapters.agents.deps import GoalDefinitionDeps, OrchestratorDeps
from kordevance.adapters.agents.goal_definition_agent import build_goal_definition_agent
from kordevance.adapters.agents.leak_guard import sanitize_agent_output
from kordevance.adapters.agents.model_resolver import ModelResolver
from kordevance.adapters.agents.persona import AGENT_PERSONA
from kordevance.adapters.agents.time_context import describe_current_datetime
from kordevance.adapters.agents.tools.get_connectors import get_connector_status
from kordevance.adapters.agents.tools.get_current_datetime_tool import get_current_datetime
from kordevance.adapters.agents.tools.proxy_relay_tools import build_callable_tools
from kordevance.domain.models.chat_turn import ChatTurn
from kordevance.domain.models.model_role import ModelRole
from kordevance.domain.ports.chat_orchestrator import ChatOrchestrator
from kordevance.domain.ports.message_store import MessageStore
from kordevance.domain.ports.proxy_relay_client import ProxyRelayClient
from kordevance.domain.services.device_service import DeviceService
from kordevance.domain.use_cases.connectors_management.handle_fetch_connectors import HandleFetchConnectors
from kordevance.domain.use_cases.goal_management.handle_create_goal import HandleCreateGoal

_ORCHESTRATOR_INSTRUCTIONS = (
    AGENT_PERSONA
    + """
[ROLE & PURPOSE]
You are Kori, the primary interface for Kordevance. For every incoming user message, evaluate the intent and choose the correct handling path.

[ROUTING PATHS]
1. GOAL DEFINITION: Route here if the user wants to achieve, track, monitor, or watch something over time. This includes both fixed targets and ongoing requests (e.g., "keep an eye on my email for X and do Y").
2. GENERAL QUERY: Route here if the request requires real-world lookups, live information, current events, or web searches.
3. DIRECT RESPONSE: Handle the message yourself if it is general conversation or a question about their active connectors. Before answering connector questions, call `get_connector_status` to verify state.

[CRITICAL CONSTRAINTS]
- Adhere strictly to your texting persona when generating text for the user.
- Never state internal path names, function names, or routing logic in user-facing text.
"""
)

_GENERAL_QUERY_INSTRUCTIONS = (
    AGENT_PERSONA
    + """
[ROLE & PURPOSE]
You are Kori answering a user request that requires real-world information.

[EXECUTION RULES]
1. TOOL GROUNDING: Use available tools to look up real-world facts before formulating an answer.
2. ACCURACY: Base your answer strictly on tool output. If tools cannot confirm the answer or return no data, state plainly that you cannot find that information right now. Never invent facts.
3. OUTPUT STYLE: State the finding concisely and plainly in your texting persona.
"""
)


class GoalDefinitionHandoff(BaseModel):
    """Route this message to the goal-definition specialist."""

    reason: str


class GeneralQueryHandoff(BaseModel):
    """Route this message to the general-query specialist."""

    reason: str


class PydanticAIChatOrchestrator(ChatOrchestrator):
    """ChatOrchestrator implementation built on pydantic-ai"""

    def __init__(
        self,
        model_resolver: ModelResolver,
        message_store: MessageStore,
        create_goal_use_case: HandleCreateGoal,
        fetch_connectors_use_case: HandleFetchConnectors,
        proxy_relay_client: ProxyRelayClient,
        device_service: DeviceService,
    ) -> None:
        self._model_resolver: ModelResolver = model_resolver
        self._message_store: MessageStore = message_store
        self._create_goal_use_case: HandleCreateGoal = create_goal_use_case
        self._fetch_connectors_use_case: HandleFetchConnectors = fetch_connectors_use_case
        self._proxy_relay_client: ProxyRelayClient = proxy_relay_client
        self._device_service: DeviceService = device_service

    async def _load_history(self, profile_id: UUID, conversation_id: UUID) -> list[ModelMessage]:
        records = await self._message_store.load_history(profile_id, conversation_id)
        messages: list[ModelMessage] = []
        for payload, _ in records:
            messages.extend(ModelMessagesTypeAdapter.validate_json(payload))
        return messages

    async def _persist_turn(
        self, profile_id: UUID, conversation_id: UUID, new_messages: list[ModelMessage], timestamp: datetime
    ) -> None:
        if not new_messages:
            return
        payload = ModelMessagesTypeAdapter.dump_json(new_messages).decode("utf-8")
        await self._message_store.append(profile_id, conversation_id, payload, timestamp)

    async def get_history(self, profile_id: UUID, conversation_id: UUID) -> list[ChatTurn]:
        records = await self._message_store.load_history(profile_id, conversation_id)
        turns: list[ChatTurn] = []
        for payload, timestamp in records:
            for message in ModelMessagesTypeAdapter.validate_json(payload):
                if isinstance(message, ModelRequest):
                    for request_part in message.parts:
                        if isinstance(request_part, UserPromptPart) and isinstance(request_part.content, str):
                            turns.append(ChatTurn(role="user", content=request_part.content, timestamp=timestamp))
                elif isinstance(message, ModelResponse):
                    for response_part in message.parts:
                        if isinstance(response_part, TextPart):
                            turns.append(ChatTurn(role="assistant", content=response_part.content, timestamp=timestamp))
        return turns

    async def handle_message(
        self, profile_id: UUID, conversation_id: UUID, message: str, timezone: str | None = None
    ) -> str:
        history = await self._load_history(profile_id, conversation_id)
        now = datetime.now(UTC)
        current_datetime_line = describe_current_datetime(now, timezone)

        triage_model = await self._model_resolver.resolve(profile_id, ModelRole.TRIAGE)
        orchestrator: Agent[OrchestratorDeps, GoalDefinitionHandoff | GeneralQueryHandoff | str] = Agent(
            model=triage_model,
            deps_type=OrchestratorDeps,
            output_type=[GoalDefinitionHandoff, GeneralQueryHandoff, str],
            instructions=_ORCHESTRATOR_INSTRUCTIONS + f"\n\nCurrent date and time: {current_datetime_line}",
            tools=[get_connector_status],
        )
        orchestrator_deps = OrchestratorDeps(
            profile_id=profile_id,
            fetch_connectors_use_case=self._fetch_connectors_use_case,
        )
        route_result = await orchestrator.run(message, message_history=history, deps=orchestrator_deps)

        if isinstance(route_result.output, GoalDefinitionHandoff):
            device = self._device_service.get_current_device()
            all_tools = await self._proxy_relay_client.get_available_tools(device, profile_id)
            proxy_tools = build_callable_tools(all_tools, profile_id, device, self._proxy_relay_client)

            primary_model = await self._model_resolver.resolve(profile_id, ModelRole.PRIMARY)
            goal_agent = build_goal_definition_agent(primary_model, now, proxy_tools, timezone)
            goal_deps = GoalDefinitionDeps(
                profile_id=profile_id,
                create_goal_use_case=self._create_goal_use_case,
                fetch_connectors_use_case=self._fetch_connectors_use_case,
            )
            goal_result = await goal_agent.run(message, message_history=history, deps=goal_deps)

            goal_new_messages = goal_result.new_messages()
            goal_output = sanitize_agent_output(goal_result.output, goal_new_messages)
            await self._persist_turn(profile_id, conversation_id, goal_new_messages, now)
            return goal_output

        if isinstance(route_result.output, GeneralQueryHandoff):
            device = self._device_service.get_current_device()
            all_tools = await self._proxy_relay_client.get_available_tools(device, profile_id)
            default_tools = [t for t in all_tools if t.is_default]
            proxy_tools = build_callable_tools(default_tools, profile_id, device, self._proxy_relay_client)

            discovery_model = await self._model_resolver.resolve(profile_id, ModelRole.DISCOVERY)
            general_agent: Agent[None, str] = Agent(
                model=discovery_model,
                output_type=str,
                instructions=_GENERAL_QUERY_INSTRUCTIONS + f"\n\nCurrent date and time: {current_datetime_line}",
                tools=[*proxy_tools, Tool(get_current_datetime)],
            )
            general_result = await general_agent.run(message, message_history=history)

            general_new_messages = general_result.new_messages()
            general_output = sanitize_agent_output(general_result.output, general_new_messages)
            await self._persist_turn(profile_id, conversation_id, general_new_messages, now)
            return general_output

        route_new_messages = route_result.new_messages()
        route_output = sanitize_agent_output(route_result.output, route_new_messages)
        await self._persist_turn(profile_id, conversation_id, route_new_messages, now)
        return route_output
