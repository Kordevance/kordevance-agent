from pydantic_ai import RunContext

from kordevance.adapters.agents.deps import GoalDefinitionDeps
from kordevance.domain.models.connectors import ConnectorTypes
from kordevance.domain.use_cases.connector_management.request_models import FetchConnectorStatusRequest


async def get_connector_status(
    ctx: RunContext[GoalDefinitionDeps], connector_types: list[ConnectorTypes]
) -> list[ConnectorTypes]:
    """Return which of the given connectors are actually connected and usable for this profile.

    Args:
        ctx: Run context carrying the profile and the connector-status use case.
        connector_types: The connectors to check — pass every connector this goal might depend on.

    Returns:
        The subset of connector_types that are genuinely connected and usable right now. Anything
        not in this list is either unconnected, connected but not assigned to this profile, or
        missing a required permission — treat all of those the same: not usable yet.
    """
    return await ctx.deps.fetch_connector_status_use_case.execute(
        FetchConnectorStatusRequest(profile_id=ctx.deps.profile_id, connector_types=connector_types)
    )
