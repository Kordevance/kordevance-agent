import logging
from datetime import UTC, datetime, timedelta
from uuid import UUID

from kordevance.domain.datetime_utils import as_aware_utc
from kordevance.domain.models.engine_source import EngineSource
from kordevance.domain.models.event import Event
from kordevance.domain.models.goal import Goal, GoalStatus, HorizonGranularity
from kordevance.domain.models.goal_cycle_finding import GoalCycleFinding
from kordevance.domain.models.goal_cycle_result import GoalCycleResult
from kordevance.domain.models.task import Task, TaskStatus
from kordevance.domain.ports.event_repository import EventRepo
from kordevance.domain.ports.goal_cycle_engine import GoalCycleEngine
from kordevance.domain.ports.goal_repository import GoalRepo
from kordevance.domain.ports.task_repository import TaskRepo
from kordevance.exceptions import ItemNotFoundError

_FINAL_REMINDER_WINDOW = timedelta(hours=24)
_TERMINAL_STATUSES = {TaskStatus.VERIFIED, TaskStatus.USER_DONE, TaskStatus.CANCELLED}
_HORIZON_PERIODS = {
    HorizonGranularity.DAY: timedelta(days=1),
    HorizonGranularity.WEEK: timedelta(weeks=1),
    HorizonGranularity.MONTH: timedelta(days=30),
}
_MAX_CONSECUTIVE_FAILURES = 5


class GoalCycleService:
    """One tick of a goal's cron job: run the goal-cycle engine, persist whatever it found, then a
    replanning pass over tasks.
    """

    def __init__(
        self,
        goal_repo: GoalRepo,
        task_repo: TaskRepo,
        event_repo: EventRepo,
        goal_cycle_engine: GoalCycleEngine,
    ) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._goal_repo: GoalRepo = goal_repo
        self._task_repo: TaskRepo = task_repo
        self._event_repo: EventRepo = event_repo
        self._goal_cycle_engine: GoalCycleEngine = goal_cycle_engine

    async def run_cycle(self, profile_id: UUID, goal_id: UUID) -> GoalCycleResult:
        goal = await self._goal_repo.fetch(profile_id, goal_id)
        result = GoalCycleResult(goal_id=goal_id)

        if goal.status != GoalStatus.ACTIVE:
            self._logger.info(f"Goal {goal_id} is '{goal.status}' — skipping cycle")
            result.notes.append(f"Goal status is '{goal.status}' — skipping cycle")
            return result

        now = datetime.now(UTC)
        deadline = as_aware_utc(goal.due_date or goal.end_at)
        is_final_attempt = now >= deadline

        if not is_final_attempt and goal.horizon_granularity is not None and goal.last_cycle_at is not None:
            period = _HORIZON_PERIODS[goal.horizon_granularity]
            if now - as_aware_utc(goal.last_cycle_at) < period:
                self._logger.info(f"Goal {goal_id} not due yet per horizon '{goal.horizon_granularity}'")
                result.notes.append(f"Not due yet per horizon '{goal.horizon_granularity}'")
                return result

        existing_tasks = await self._task_repo.fetch_all_for_goal(profile_id, goal_id)

        try:
            still_active = await self._run_engine(goal, existing_tasks, result, now, is_final_attempt)
        except Exception as error:
            await self._handle_cycle_failure(goal, result, error)
            return result

        if not still_active:
            return result

        existing_tasks = await self._task_repo.fetch_all_for_goal(profile_id, goal_id)
        self._replan(existing_tasks, result)

        goal.consecutive_failures = 0
        goal.last_cycle_at = now
        await self._goal_repo.update(goal)

        return result

    async def _handle_cycle_failure(self, goal: Goal, result: GoalCycleResult, error: Exception) -> None:
        self._logger.exception(f"Goal cycle failed for goal {goal.id}", exc_info=error)
        goal.consecutive_failures += 1
        result.notes.append(f"Cycle failed: {error}")

        if goal.consecutive_failures >= _MAX_CONSECUTIVE_FAILURES:
            goal.status = GoalStatus.PAUSED
            result.notes.append(f"Goal paused after {goal.consecutive_failures} consecutive failed cycles")

        await self._goal_repo.update(goal)

    async def _goal_still_active(self, profile_id: UUID, goal_id: UUID) -> bool:
        try:
            current = await self._goal_repo.fetch(profile_id, goal_id)
        except ItemNotFoundError:
            return False
        return current.status == GoalStatus.ACTIVE

    async def _run_engine(
        self,
        goal: Goal,
        existing_tasks: list[Task],
        result: GoalCycleResult,
        now: datetime,
        is_final_attempt: bool,
    ) -> bool:
        finding = await self._goal_cycle_engine.run(
            goal=goal,
            profile_id=goal.profile_id,
            existing_tasks=existing_tasks,
            is_final_attempt=is_final_attempt,
        )

        if not finding.candidates and not finding.completed_tasks:
            self._logger.info(f"Goal cycle engine found nothing for goal {goal.id} this cycle: {finding.summary}")
            result.notes.append(finding.summary)
            return True

        if not await self._goal_still_active(goal.profile_id, goal.id):
            self._logger.info(f"Goal {goal.id} no longer active — discarding this cycle's findings")
            result.notes.append("Goal no longer active — discarding this cycle's findings")
            return False

        event = await self._persist_finding_event(goal, finding, now)
        result.events_created.append(event.id)

        await self._persist_completions(existing_tasks, finding, event.id, result)
        await self._persist_candidates(goal, existing_tasks, finding, event.id, result)

        return True

    async def _persist_finding_event(self, goal: Goal, finding: GoalCycleFinding, now: datetime) -> Event:
        event = Event(
            profile_id=goal.profile_id,
            goal_id=goal.id,
            engine_source=EngineSource.AGENT,
            raw_content=finding.summary,
            occurred_at=now,
            classified_type="goal_cycle_finding",
            extracted_fields={
                "candidates": [candidate.model_dump(mode="json") for candidate in finding.candidates],
                "completed_tasks": [signal.model_dump(mode="json") for signal in finding.completed_tasks],
            },
        )
        await self._event_repo.save(event)
        return event

    async def _persist_completions(
        self,
        existing_tasks: list[Task],
        finding: GoalCycleFinding,
        event_id: UUID,
        result: GoalCycleResult,
    ) -> None:
        tasks_by_id = {task.id: task for task in existing_tasks}

        for signal in finding.completed_tasks:
            task = tasks_by_id.get(signal.task_id)
            if task is None or task.status in _TERMINAL_STATUSES:
                continue
            if (
                task.status == TaskStatus.INFERRED_DONE
                and task.status_confidence is not None
                and task.status_confidence >= signal.confidence
            ):
                continue

            task.status = TaskStatus.INFERRED_DONE
            task.status_confidence = signal.confidence
            task.provenance_event_id = event_id
            task.updated_at = datetime.now(UTC)
            await self._task_repo.update(task)
            result.tasks_updated.append(task.id)

    async def _persist_candidates(
        self,
        goal: Goal,
        existing_tasks: list[Task],
        finding: GoalCycleFinding,
        event_id: UUID,
        result: GoalCycleResult,
    ) -> None:
        already_surfaced_titles = {task.title for task in existing_tasks if task.source_type == EngineSource.AGENT}
        goal_start = as_aware_utc(goal.start_at)
        goal_end = as_aware_utc(goal.end_at)

        for candidate in finding.candidates:
            if candidate.title in already_surfaced_titles:
                continue

            due_date = candidate.due_date
            if due_date is not None:
                due_date = as_aware_utc(due_date)
                if not (goal_start <= due_date <= goal_end):
                    due_date = None

            task = Task(
                goal_id=goal.id,
                profile_id=goal.profile_id,
                title=candidate.title,
                description=candidate.description,
                due_date=due_date or goal.due_date,
                status=TaskStatus.PENDING,
                status_confidence=candidate.confidence,
                source_type=EngineSource.AGENT,
                provenance_event_id=event_id,
            )
            await self._task_repo.save(task)
            result.tasks_created.append(task.id)

    def _replan(self, tasks: list[Task], result: GoalCycleResult) -> None:
        now = datetime.now(UTC)

        for task in tasks:
            if task.status in _TERMINAL_STATUSES or task.due_date is None:
                continue
            if as_aware_utc(task.due_date) - now <= _FINAL_REMINDER_WINDOW:
                result.tasks_needing_final_reminder.append(task.id)
