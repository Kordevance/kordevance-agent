from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from kordevance.adapters.scheduler.apscheduler_job_scheduler import APSchedulerJobScheduler
from kordevance.application import _WORKING_DIRECTORY
from kordevance.application.jobs.goal_cycle_job import run_goal_cycle_job
from kordevance.domain.ports.job_scheduler import JobScheduler

_DB_PATH = _WORKING_DIRECTORY.joinpath("kordevance.db")


@lru_cache(maxsize=1)
def get_job_scheduler() -> JobScheduler:
    return APSchedulerJobScheduler(db_path=_DB_PATH, job_func=run_goal_cycle_job)


JobSchedulerDep = Annotated[JobScheduler, Depends(get_job_scheduler)]
