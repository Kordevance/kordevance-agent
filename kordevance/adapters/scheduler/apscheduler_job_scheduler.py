import logging
from collections.abc import Awaitable, Callable
from pathlib import Path
from uuid import UUID

from apscheduler.jobstores.base import JobLookupError
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from kordevance.domain.ports.job_scheduler import JobScheduler

_JOB_ID_PREFIX = "goal-cycle:"


class APSchedulerJobScheduler(JobScheduler):
    def __init__(self, db_path: Path, job_func: Callable[[str, str], Awaitable[None]]) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._job_func: Callable[[str, str], Awaitable[None]] = job_func
        self._scheduler: AsyncIOScheduler = AsyncIOScheduler(
            jobstores={"default": SQLAlchemyJobStore(url=f"sqlite:///{db_path}")}
        )

    @staticmethod
    def _job_id(goal_id: UUID) -> str:
        return f"{_JOB_ID_PREFIX}{goal_id}"

    def start(self) -> None:
        self._logger.info("Starting job scheduler")
        self._scheduler.start()

    def shutdown(self) -> None:
        self._logger.info("Shutting down job scheduler")
        self._scheduler.shutdown(wait=False)

    def schedule_goal_cycle(self, profile_id: UUID, goal_id: UUID, interval_seconds: int) -> None:
        self._logger.info(f"Scheduling goal cycle for goal {goal_id} every {interval_seconds}s")
        self._scheduler.add_job(
            func=self._job_func,
            trigger="interval",
            seconds=interval_seconds,
            id=self._job_id(goal_id),
            args=[str(profile_id), str(goal_id)],
            replace_existing=True,
            coalesce=True,
            misfire_grace_time=interval_seconds,
        )

    def unschedule_goal_cycle(self, goal_id: UUID) -> None:
        self._logger.info(f"Unscheduling goal cycle for goal {goal_id}")
        try:
            self._scheduler.remove_job(self._job_id(goal_id))
        except JobLookupError:
            self._logger.info(f"No scheduled job for goal {goal_id} — already unscheduled")
