from datetime import datetime

from pydantic_ai import RunContext

from kordevance.adapters.agents.deps import GoalDefinitionDeps
from kordevance.domain.models.connectors import Connector
from kordevance.domain.models.goal import HorizonGranularity, ProgressMetricType
from kordevance.domain.use_cases.goal_management.request_models import CreateGoalRequest


async def create_goal(
    ctx: RunContext[GoalDefinitionDeps],
    title: str,
    domain: str,
    start_at: str,
    end_at: str,
    horizon_granularity: HorizonGranularity,
    progress_metric_type: ProgressMetricType,
    description: str | None = None,
    due_date: str | None = None,
    target_value: float | None = None,
    required_connectors: list[Connector] | None = None,
) -> str:
    """Create the goal once every required field has a confident, user-confirmed value.

    Do not call this while any information is missing, ambiguous, or unconfirmed by the user.
    Ask a clarifying question in your normal response instead. Every connector listed in
    required_connectors must be either genuinely connected (per get_connector_status) or
    explicitly waived by the user in the conversation before this is called.

    Args:
        ctx: Run context carrying the profile and the goal-creation use case.
        title: Short, human-readable name for the goal.
        domain: Free-text label for what kind of goal this is, e.g. "exam_prep", "fitness".
        start_at: ISO 8601 datetime the goal work begins.
        end_at: ISO 8601 datetime of the goal's hard deadline.
        horizon_granularity: Planning detail-window size for this goal.
        progress_metric_type: How progress is measured.
        description: Optional longer description of the goal.
        due_date: Optional ISO 8601 datetime for a decision/action deadline that is earlier than
            end_at — set this only when the user names a date by which they need an answer or
            result, separate from the goal's own end date (e.g. "find me flights for a trip in
            December, but tell me what you've got by November 12th" -> due_date is November 12th,
            end_at is the trip's own end). Leave unset when no such earlier deadline was named.
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
        )
    )
    return f"Goal '{goal.title}' created (id={goal.id})."
