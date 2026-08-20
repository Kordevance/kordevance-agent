from pydantic_ai import RunContext

from kordevance.adapters.agents.deps import GoalDefinitionDeps


async def get_connector_status(ctx: RunContext[GoalDefinitionDeps]) -> str:
    """Check which connectors the user actually has connected right now.

    Call this whenever the goal plausibly depends on a connector (e.g. tracking via a calendar
    or a fitness app) before deciding what to put in required_connectors. It returns every
    connector the user could use, each tagged as connected or not-yet-connected.

    Returns:
        A line per connector in the form "<provider> / <category>: connected" or
        "<provider> / <category>: not connected".
    """
    connectors = await ctx.deps.fetch_connectors_use_case.execute(ctx.deps.profile_id)
    if not connectors:
        return "No connectors are available."

    return "\n".join(
        f"{connector.provider} / {connector.category}: {'connected' if connector.active else 'not connected'}"
        for connector in connectors
    )
