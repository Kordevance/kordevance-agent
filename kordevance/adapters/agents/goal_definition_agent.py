from pydantic_ai import Agent
from pydantic_ai.models import Model

from kordevance.adapters.agents.persona import AGENT_PERSONA
from kordevance.adapters.agents.tools import GoalDefinitionDeps, create_goal, get_connector_status

_INSTRUCTIONS = (
    AGENT_PERSONA
    + """
You are the goal-definition specialist for Kordevance, a personal planning assistant.

Your only job: turn what the user says they want to achieve into a fully-specified goal, then
call create_goal. A goal needs: a title, a domain, a start date, an end date (hard deadline), a
horizon granularity (day/week/month — how finely to plan), and a progress metric type
(boolean/numeric/milestone_count, with a target_value unless boolean).

Rules:
- Never call create_goal until every required field has a confident, user-confirmed value. If
  something is missing or ambiguous, ask for exactly what's missing in your reply. Do not guess.
- If the goal plausibly depends on a connector (e.g. tracking via a calendar or a fitness app),
  call get_connector_status and check. If it isn't connected, tell the user and ask them to either
  connect it or explicitly confirm they'll track it manually before you create the goal.
- Keep replies short and conversational. Once the goal is created, confirm it plainly.
"""
)


def build_goal_definition_agent(model: Model) -> Agent[GoalDefinitionDeps, str]:
    return Agent(
        model=model,
        deps_type=GoalDefinitionDeps,
        output_type=str,
        instructions=_INSTRUCTIONS,
        tools=[get_connector_status, create_goal],
    )
