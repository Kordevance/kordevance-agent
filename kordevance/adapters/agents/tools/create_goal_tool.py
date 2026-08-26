from datetime import datetime

from pydantic_ai import RunContext

from kordevance.adapters.agents.deps import GoalDefinitionDeps
from kordevance.domain.models.connectors import Connector
from kordevance.domain.models.goal import HorizonGranularity, ProgressMetricType
from kordevance.domain.models.tz import TimezoneMode
from kordevance.domain.use_cases.goal_management.request_models import CreateGoalRequest


async def create_goal(
    ctx: RunContext[GoalDefinitionDeps],
    title: str,
    domain: str,
    start_at: str,
    end_at: str,
    progress_metric_type: ProgressMetricType,
    timezone_mode: TimezoneMode,
    specific_timezone: str | None = None,
    horizon_granularity: HorizonGranularity | None = None,
    description: str | None = None,
    due_date: str | None = None,
    target_value: float | None = None,
    required_connectors: list[Connector] | None = None,
) -> str:
    """Create a new goal only when all necessary execution context has been gathered.

    CRITICAL CONSTRAINT: Before calling this tool, you must evaluate the user's request.
    If a separate agent were to read only the title and description, would they have enough
    specific information to execute the task without asking follow-up questions?
    If the answer is no (e.g., the user gave a broad intent but omitted necessary locations,
    budgets, specific subjects, or constraints), do not call this tool. Ask clarifying
    questions first.

    Every connector listed in required_connectors must be genuinely connected or explicitly
    waived by the user before calling this function.

    Args:
        ctx: Run context carrying the profile and the goal-creation use case.
        title: A short, human-readable name for the goal.
        domain: A free-text categorical label for the goal type.
        start_at: ISO 8601 datetime the goal work begins.
        end_at: ISO 8601 datetime of the goal's final hard deadline.
        horizon_granularity: Optional. Set this only if the user explicitly requests a
            specific check-in cadence (daily, weekly, monthly). Do not infer this from
            the domain. Leave unset by default.
        progress_metric_type: How progress is measured.
        timezone_mode: Categorize time sensitivity. Set to "floating" for habits or routines
            that follow the user's dynamic location, "home" for tasks anchored strictly to
            their primary residence, "fixed" for tasks tied to a specific destination region.
        specific_timezone: Optional IANA timezone string (e.g., "Asia/Tokyo", "Africa/Casablanca").
            Required ONLY when timezone_mode is set to "fixed". Leave unset otherwise.
        description: A comprehensive, self-contained brief of the goal. This must include
            all domain-specific facts, constraints, and parameters gathered from the user
            that are required to actually execute the work. Do not simply restate the title.
        due_date: Optional ISO 8601 datetime for an intermediate decision or action deadline.
            Set this only if the user specifies an early milestone distinct from the end_at
            date. Leave unset otherwise.
        target_value: Required unless progress_metric_type is "boolean".
        required_connectors: Connectors this goal's tracking depends on, if any.

    Returns:
        A short confirmation message naming the created goal.
    """
    goal = await ctx.deps.create_goal_use_case.execute(
        CreateGoalRequest(
            profile_id=ctx.deps.profile_id,
            title=title,
            description=description,
            domain=domain,
            start_at=datetime.fromisoformat(start_at),
            end_at=datetime.fromisoformat(end_at),
            horizon_granularity=horizon_granularity,
            due_date=datetime.fromisoformat(due_date) if due_date else None,
            progress_metric_type=progress_metric_type,
            target_value=target_value,
            required_connectors=required_connectors or [],
            timezone_mode=timezone_mode,
            specific_timezone=specific_timezone,
        )
    )
    return f"Goal '{goal.title}' created (id={goal.id})."
