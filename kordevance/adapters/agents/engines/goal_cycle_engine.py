import logging
import re
from typing import Any
from uuid import UUID

from pydantic_ai import Agent, RunContext
from pydantic_ai.tools import Tool

from kordevance.adapters.agents.model_resolver import ModelResolver
from kordevance.adapters.agents.persona import AGENT_PERSONA
from kordevance.adapters.agents.tools.get_current_datetime_tool import get_current_datetime
from kordevance.domain.models.goal import Goal
from kordevance.domain.models.goal_cycle_finding import GoalCycleFinding
from kordevance.domain.models.goal_cycle_triage import GoalCycleTriageDecision
from kordevance.domain.models.model_role import ModelRole
from kordevance.domain.models.task import Task
from kordevance.domain.models.tool import ToolDefinition
from kordevance.domain.ports.goal_cycle_engine import GoalCycleEngine
from kordevance.domain.ports.proxy_relay_client import ProxyRelayClient
from kordevance.domain.services.device_service import DeviceService

# Below this confidence on any candidate/completion, the draft goes to a PRIMARY-tier review pass
# before being trusted (same threshold that would otherwise leave a task's status ambiguous.)
_REVIEW_CONFIDENCE_THRESHOLD = 0.75

# ProxyRelay tool names are dotted (e.g. "calendar.create_event") and some providers (e.g Anthropic)
# reject that in a tool name (must match ^[a-zA-Z0-9_-]{1,128}$). Only the LLM-facing name needs
# sanitizing. Note: The real dotted name is still what gets sent to execute_tool.
_INVALID_TOOL_NAME_CHARS = re.compile(r"[^a-zA-Z0-9_-]")


def _sanitize_tool_name(name: str) -> str:
    return _INVALID_TOOL_NAME_CHARS.sub("_", name)[:128]

_TRIAGE_INSTRUCTIONS = (
    AGENT_PERSONA
    + """
You decide whether a personal planning goal is worth spending a real reasoning turn on right now,
during one scheduled check-in. You have no tools — decide from the goal and its current tasks
alone.

Say should_explore=True only if there's a concrete reason to look for something new or to check on
existing tasks right now (e.g. a task is pending with no attempt yet, or enough may plausibly have
changed since the last check). Say False when there's nothing new to look for and nothing pending
that recently checking again would help — most checks should come back False. Be conservative:
false negatives cost nothing (there will be another check-in), false positives cost a real turn.
"""
)

_EXPLORE_INSTRUCTIONS = (
    AGENT_PERSONA
    + """
You are the goal-cycle engine for Kordevance, a personal planning assistant. Given a goal, its
preferences, its current tasks, and whatever tools are available for it, use those tools to find
out what's actually true right now and report back.

This covers two kinds of outcome in one pass, whichever the tools available make possible:
- New candidates: something that satisfies the goal and wasn't known before (e.g. a course, a
  flight). Only propose one as a genuine match if it actually satisfies the goal's stated
  preferences/constraints — a mediocre option isn't worth surfacing on an ordinary cycle. Never
  repeat a candidate already listed under "already surfaced".
- Completed tasks: clear evidence (via a tool) that one of the existing tasks is now done.
  "Clear evidence" means don't guess from something ambiguous — leave it alone if unsure.

Rules:
- Use the available tools to find out — don't invent results.
- Tools listed as "requires confirmation" are not callable — never attempt to call them. Only
  describe what you'd want to do with one, in your summary, so the user can confirm it later.
- If this is explicitly marked as the FINAL attempt, you must return your best available
  candidates even if none fully satisfy the preferences — say so plainly in the summary. Otherwise
  return nothing rather than a weak match; there will be another cycle.
"""
)

_REVIEW_INSTRUCTIONS = (
    AGENT_PERSONA
    + """
You are reviewing a draft finding from a goal-cycle engine before it gets acted on. It was flagged
for review because it contains a low-confidence candidate or task-completion signal, or because
this was a final attempt. You have no tools — judge only from the goal, its tasks, and the draft.

Return a revised finding: drop or adjust anything that doesn't actually hold up, keep anything
that does. If the draft is already sound, return it unchanged. Never raise a candidate's or a
completion's confidence beyond what the draft's own summary actually supports.
"""
)


class PydanticAIGoalCycleEngine(GoalCycleEngine):
    def __init__(
        self,
        model_resolver: ModelResolver,
        proxy_relay_client: ProxyRelayClient,
        device_service: DeviceService,
    ) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._model_resolver: ModelResolver = model_resolver
        self._proxy_relay_client: ProxyRelayClient = proxy_relay_client
        self._device_service: DeviceService = device_service

    @staticmethod
    def _tasks_context(existing_tasks: list[Task]) -> str:
        return (
            "\n".join(
                f"- id={task.id} title={task.title!r} status={task.status} "
                f"confidence={task.status_confidence} due_date={task.due_date}"
                for task in existing_tasks
            )
            or "(no existing tasks for this goal)"
        )

    @staticmethod
    def _goal_context(goal: Goal, is_final_attempt: bool) -> str:
        return f"""
Goal: {goal.title}
Goal description/preferences: {goal.description or "(none)"}
Goal domain: {goal.domain}
Deadline for a result: {(goal.due_date or goal.end_at).isoformat()}
This is the FINAL attempt: {is_final_attempt}
"""

    def _build_callable_tool(self, tool_def: ToolDefinition, profile_id: UUID) -> Tool[None]:
        async def _call(_ctx: RunContext[None], **kwargs: Any) -> Any:
            device = self._device_service.get_current_device()
            return await self._proxy_relay_client.execute_tool(device, profile_id, tool_def.name, dict(kwargs))

        return Tool.from_schema(
            function=_call,
            name=_sanitize_tool_name(tool_def.name),
            description=tool_def.description,
            json_schema=tool_def.input_schema,
            takes_ctx=True,
        )

    async def _should_explore(
        self, goal: Goal, profile_id: UUID, existing_tasks: list[Task], is_final_attempt: bool
    ) -> GoalCycleTriageDecision:
        if is_final_attempt:
            return GoalCycleTriageDecision(should_explore=True, reason="Final attempt — always explore.")

        model = await self._model_resolver.resolve(profile_id, ModelRole.TRIAGE)
        agent: Agent[None, GoalCycleTriageDecision] = Agent(
            model=model, output_type=GoalCycleTriageDecision, instructions=_TRIAGE_INSTRUCTIONS
        )
        prompt = (
            self._goal_context(goal, is_final_attempt) + f"\nExisting tasks:\n{self._tasks_context(existing_tasks)}"
        )
        result = await agent.run(prompt)
        return result.output

    async def _explore(
        self, goal: Goal, profile_id: UUID, existing_tasks: list[Task], is_final_attempt: bool
    ) -> GoalCycleFinding:
        device = self._device_service.get_current_device()
        all_tools = await self._proxy_relay_client.get_available_tools(device, profile_id)

        callable_tools = [self._build_callable_tool(t, profile_id) for t in all_tools if not t.requires_confirmation]
        confirmation_only_tools = [t for t in all_tools if t.requires_confirmation]

        if not callable_tools:
            return GoalCycleFinding(summary="No usable tools are currently available for this goal's connectors.")

        model = await self._model_resolver.resolve(profile_id, ModelRole.DISCOVERY)
        agent: Agent[None, GoalCycleFinding] = Agent(
            model=model,
            output_type=GoalCycleFinding,
            instructions=_EXPLORE_INSTRUCTIONS,
            tools=[*callable_tools, Tool(get_current_datetime)],
        )

        already_surfaced = (
            "\n".join(f"- {task.title}: {task.description}" for task in existing_tasks) or "(nothing surfaced yet)"
        )
        confirmation_only_desc = "\n".join(f"- {t.name}: {t.description}" for t in confirmation_only_tools) or "(none)"
        prompt = (
            self._goal_context(goal, is_final_attempt)
            + f"""
Existing tasks:
{self._tasks_context(existing_tasks)}

Already surfaced candidates for this goal:
{already_surfaced}

Tools requiring confirmation (describe only, never call):
{confirmation_only_desc}
"""
        )
        result = await agent.run(prompt)
        return result.output

    @staticmethod
    def _needs_review(finding: GoalCycleFinding, is_final_attempt: bool) -> bool:
        if is_final_attempt:
            return True
        return any(c.confidence < _REVIEW_CONFIDENCE_THRESHOLD for c in finding.candidates) or any(
            c.confidence < _REVIEW_CONFIDENCE_THRESHOLD for c in finding.completed_tasks
        )

    async def _review(
        self,
        goal: Goal,
        profile_id: UUID,
        existing_tasks: list[Task],
        is_final_attempt: bool,
        draft: GoalCycleFinding,
    ) -> GoalCycleFinding:
        model = await self._model_resolver.resolve(profile_id, ModelRole.PRIMARY)
        agent: Agent[None, GoalCycleFinding] = Agent(
            model=model, output_type=GoalCycleFinding, instructions=_REVIEW_INSTRUCTIONS
        )
        prompt = (
            self._goal_context(goal, is_final_attempt)
            + f"\nExisting tasks:\n{self._tasks_context(existing_tasks)}"
            + f"\nDraft finding to review:\n{draft.model_dump_json()}"
        )
        result = await agent.run(prompt)
        return result.output

    async def run(
        self,
        goal: Goal,
        profile_id: UUID,
        existing_tasks: list[Task],
        is_final_attempt: bool,
    ) -> GoalCycleFinding:
        triage = await self._should_explore(goal, profile_id, existing_tasks, is_final_attempt)
        if not triage.should_explore:
            return GoalCycleFinding(summary=triage.reason)

        draft = await self._explore(goal, profile_id, existing_tasks, is_final_attempt)

        if self._needs_review(draft, is_final_attempt):
            return await self._review(goal, profile_id, existing_tasks, is_final_attempt, draft)

        return draft
