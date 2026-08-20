import logging
from datetime import UTC, datetime, timedelta
from uuid import UUID

from kordevance.domain.models.engine_source import EngineSource
from kordevance.domain.models.event import Event
from kordevance.domain.models.goal import Goal, GoalStatus
from kordevance.domain.models.goal_cycle_finding import GoalCycleFinding
from kordevance.domain.models.goal_cycle_result import GoalCycleResult
from kordevance.domain.models.task import Task, TaskStatus
from kordevance.domain.ports.event_repository import EventRepo
from kordevance.domain.ports.goal_cycle_engine import GoalCycleEngine
from kordevance.domain.ports.goal_repository import GoalRepo
from kordevance.domain.ports.task_repository import TaskRepo

_FINAL_REMINDER_WINDOW = timedelta(hours=24)
_TERMINAL_STATUSES = {TaskStatus.VERIFIED, TaskStatus.USER_DONE, TaskStatus.CANCELLED}


def _as_aware_utc(value: datetime) -> datetime:
    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)


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

        existing_tasks = await self._task_repo.fetch_all_for_goal(profile_id, goal_id)

        await self._run_engine(goal, existing_tasks, result)
        existing_tasks = await self._task_repo.fetch_all_for_goal(profile_id, goal_id)

        self._replan(existing_tasks, result)

        return result

    async def _run_engine(self, goal: Goal, existing_tasks: list[Task], result: GoalCycleResult) -> None:
        now = datetime.now(UTC)
        deadline = _as_aware_utc(goal.due_date or goal.end_at)
        is_final_attempt = now >= deadline

        finding = await self._goal_cycle_engine.run(
            goal=goal,
            profile_id=goal.profile_id,
            existing_tasks=existing_tasks,
            is_final_attempt=is_final_attempt,
        )

        if not finding.candidates and not finding.completed_tasks:
            self._logger.info(f"Goal cycle engine found nothing for goal {goal.id} this cycle: {finding.summary}")
            result.notes.append(finding.summary)
            return

        event = await self._persist_finding_event(goal, finding, now)
        result.events_created.append(event.id)

        await self._persist_completions(existing_tasks, finding, event.id, result)
        await self._persist_candidates(goal, existing_tasks, finding, event.id, result)

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

        for candidate in finding.candidates:
            if candidate.title in already_surfaced_titles:
                continue

            task = Task(
                goal_id=goal.id,
                profile_id=goal.profile_id,
                title=candidate.title,
                description=candidate.description,
                due_date=candidate.due_date or goal.due_date,
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
            if _as_aware_utc(task.due_date) - now <= _FINAL_REMINDER_WINDOW:
                result.tasks_needing_final_reminder.append(task.id)
