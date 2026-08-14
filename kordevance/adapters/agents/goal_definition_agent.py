from pydantic_ai import Agent
from pydantic_ai.models import Model

from kordevance.adapters.agents.deps import GoalDefinitionDeps
from kordevance.adapters.agents.persona import AGENT_PERSONA
from kordevance.adapters.agents.tools.create_goal_tool import create_goal

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
  ask the user which ones and record them in required_connectors — there is no live connector
  status to check yet, so take the user's word for what they intend to connect.
- Keep replies short and conversational. Once the goal is created, confirm it plainly.
"""
)


def build_goal_definition_agent(model: Model) -> Agent[GoalDefinitionDeps, str]:
    return Agent(
        model=model,
        deps_type=GoalDefinitionDeps,
        output_type=str,
        instructions=_INSTRUCTIONS,
        tools=[create_goal],
    )
