import logging
from uuid import UUID

from kordevance.application.dependencies.goal_cycle import get_goal_cycle_engine_standalone
from kordevance.application.dependencies.sql_store_adapter import (
    get_event_repository,
    get_goal_repository,
    get_profile_repository,
    get_task_repository,
)
from kordevance.domain.use_cases.goal_cycle_management.handle_run_goal_cycle import HandleRunGoalCycle
from kordevance.domain.use_cases.goal_cycle_management.request_models import RunGoalCycleRequest

_logger = logging.getLogger(__name__)


async def run_goal_cycle_job(profile_id: str, goal_id: str) -> None:
    use_case = HandleRunGoalCycle(
        goal_repo=get_goal_repository(),
        task_repo=get_task_repository(),
        event_repo=get_event_repository(),
        goal_cycle_engine=get_goal_cycle_engine_standalone(),
        profile_repo=get_profile_repository(),
    )

    try:
        result = await use_case.execute(RunGoalCycleRequest(profile_id=UUID(profile_id), goal_id=UUID(goal_id)))
        _logger.info(
            f"Goal cycle for {goal_id}: {len(result.tasks_created)} created, "
            f"{len(result.tasks_updated)} updated, {len(result.tasks_needing_final_reminder)} need a final reminder"
        )
    except Exception as e:
        # A single bad cycle must never take the scheduler down. log and let the next tick retry.
        _logger.exception(f"Goal cycle failed for goal {goal_id}")
        _logger.exception(e)
