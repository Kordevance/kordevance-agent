import logging
from datetime import UTC, datetime
from uuid import UUID

from pydantic_ai import Agent
from pydantic_ai.tools import Tool

from kordevance.adapters.agents.model_resolver import ModelResolver
from kordevance.adapters.agents.time_context import describe_current_datetime
from kordevance.adapters.agents.tools.get_current_datetime_tool import get_current_datetime
from kordevance.adapters.agents.tools.proxy_relay_tools import build_callable_tools
from kordevance.domain.models.goal import Goal
from kordevance.domain.models.goal_cycle_finding import GoalCycleFinding
from kordevance.domain.models.goal_cycle_triage import GoalCycleTriageDecision
from kordevance.domain.models.model_role import ModelRole
from kordevance.domain.models.task import Task
from kordevance.domain.ports.goal_cycle_engine import GoalCycleEngine
from kordevance.domain.ports.proxy_relay_client import ProxyRelayClient
from kordevance.domain.services.device_service import DeviceService

# Below this confidence on any candidate/completion, the draft goes to a PRIMARY-tier review pass
# before being trusted (same threshold that would otherwise leave a task's status ambiguous.)
_REVIEW_CONFIDENCE_THRESHOLD = 0.75

_TRIAGE_INSTRUCTIONS = """[ROLE & CONTEXT]
You are a conservative triage evaluator for a goal-cycle engine. You decide if a goal requires active inspection during this scheduled check-in. You have no tool access.

[OBJECTIVE]
Determine whether spending a reasoning turn is necessary based strictly on the goal definition and its current tasks.

[EVALUATION RULES]
- Return should_explore = True ONLY IF there is a concrete, immediate reason to inspect external state (e.g., a pending task has zero prior attempts, or external state is likely to have changed).
- Return should_explore = False IF no tasks are pending and no state changes are expected.
- DEFAULT TO FALSE. False negatives cost nothing because another check-in will occur later. False positives waste real computational cycles.
"""


_EXPLORE_INSTRUCTIONS = """[ROLE & CONTEXT]
You are the goal-cycle execution engine for Kordevance. Given a goal, its preferences, current tasks, and available tools, inspect real-world state and compute updates.

[PERMITTED OUTCOMES]
1. New Candidates: Identify new items satisfying goal constraints. Propose a candidate ONLY IF it meets all stated preferences. Reject mediocre options. Do not re-propose items listed under "already surfaced".
2. Completed Tasks: Verify task completion using direct tool evidence. Require clear proof before marking a task complete.

[CRITICAL CONSTRAINTS]
- TOOL GROUNDING: Base findings strictly on tool outputs. Never invent facts, entities, or parameters.
- PRECISION MATCHING: Match the exact granularity provided by the source. If a source gives a date without a specific time, do not invent a time. Represent all-day items by spanning 00:00 to 23:59, and explicitly state in the summary that exact time precision was missing.
- UNCONFIRMED TOOLS: Never attempt to call tools marked "requires confirmation". Describe the intended action in your summary payload so the orchestrator can request user confirmation.
- FINAL ATTEMPT OVERRIDE: If flagged as the FINAL attempt, return the best available candidates even if preferences are partially met, and state this trade-off clearly in the summary payload. Otherwise, return nothing if matches are weak.
"""


_REVIEW_INSTRUCTIONS = """[ROLE & CONTEXT]
You are the quality auditor for draft goal findings. You judge findings flagged for low confidence or final-attempt status before they are saved or acted upon. You have no tool access.

[OBJECTIVE]
Review the draft payload against the goal and tasks, then return a revised finding payload.

[AUDIT RULES]
- EVIDENCE VERIFICATION: Drop or adjust any candidate or task-completion signal that is not fully supported by the draft evidence. Keep valid findings unchanged.
- CONFIDENCE CAP: Never raise confidence or certainty levels beyond what the draft summary explicitly supports.
- PRECISION AUDIT: Scan for fabricated precision (such as specific times, budgets, or locations presented as fact when the evidence is vague). Correct fabricated details back to the actual precision level shown in the evidence.
"""


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
    def _goal_context(goal: Goal, is_final_attempt: bool, timezone: str) -> str:
        return f"""
                    Current date and time: {describe_current_datetime(datetime.now(UTC), timezone)}
                    Goal: {goal.title}
                    Goal description/preferences: {goal.description or "(none)"}
                    Goal domain: {goal.domain}
                    Deadline for a result: {(goal.due_date or goal.end_at).isoformat()}
                    This is the FINAL attempt: {is_final_attempt}
                """

    async def _should_explore(
        self, goal: Goal, profile_id: UUID, existing_tasks: list[Task], is_final_attempt: bool, timezone: str
    ) -> GoalCycleTriageDecision:
        if is_final_attempt:
            return GoalCycleTriageDecision(should_explore=True, reason="Final attempt, always explore.")

        model = await self._model_resolver.resolve(profile_id, ModelRole.TRIAGE)
        agent: Agent[None, GoalCycleTriageDecision] = Agent(
            model=model, output_type=GoalCycleTriageDecision, instructions=_TRIAGE_INSTRUCTIONS
        )
        prompt = (
            self._goal_context(goal, is_final_attempt, timezone)
            + f"\nExisting tasks:\n{self._tasks_context(existing_tasks)}"
        )
        result = await agent.run(prompt)
        return result.output

    async def _explore(
        self, goal: Goal, profile_id: UUID, existing_tasks: list[Task], is_final_attempt: bool, timezone: str
    ) -> GoalCycleFinding:
        device = self._device_service.get_current_device()
        all_tools = await self._proxy_relay_client.get_available_tools(device, profile_id)

        callable_tools = build_callable_tools(all_tools, profile_id, device, self._proxy_relay_client)
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
            self._goal_context(goal, is_final_attempt, timezone)
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
        timezone: str,
    ) -> GoalCycleFinding:
        model = await self._model_resolver.resolve(profile_id, ModelRole.PRIMARY)
        agent: Agent[None, GoalCycleFinding] = Agent(
            model=model, output_type=GoalCycleFinding, instructions=_REVIEW_INSTRUCTIONS
        )
        prompt = (
            self._goal_context(goal, is_final_attempt, timezone)
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
        timezone: str,
    ) -> GoalCycleFinding:
        triage = await self._should_explore(goal, profile_id, existing_tasks, is_final_attempt, timezone)
        if not triage.should_explore:
            return GoalCycleFinding(summary=triage.reason)

        draft = await self._explore(goal, profile_id, existing_tasks, is_final_attempt, timezone)

        if self._needs_review(draft, is_final_attempt):
            return await self._review(goal, profile_id, existing_tasks, is_final_attempt, draft, timezone)

        return draft
