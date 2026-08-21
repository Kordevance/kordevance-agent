from typing import Annotated

from fastapi import Depends

from kordevance.application.dependencies.scheduler import JobSchedulerDep
from kordevance.application.dependencies.sql_store_adapter import GoalRepoDep
from kordevance.domain.use_cases.goal_management.handle_create_goal import HandleCreateGoal
from kordevance.domain.use_cases.goal_management.handle_delete_goal import HandleDeleteGoal
from kordevance.domain.use_cases.goal_management.handle_fetch_goals import HandleFetchGoals


def get_create_goal_use_case(goal_repo: GoalRepoDep, job_scheduler: JobSchedulerDep) -> HandleCreateGoal:
    return HandleCreateGoal(repository=goal_repo, job_scheduler=job_scheduler)


def get_fetch_goals_use_case(goal_repo: GoalRepoDep) -> HandleFetchGoals:
    return HandleFetchGoals(repository=goal_repo)


def get_delete_goal_use_case(goal_repo: GoalRepoDep, job_scheduler: JobSchedulerDep) -> HandleDeleteGoal:
    return HandleDeleteGoal(repository=goal_repo, job_scheduler=job_scheduler)


CreateGoalUseCaseDep = Annotated[HandleCreateGoal, Depends(get_create_goal_use_case)]
FetchGoalsUseCaseDep = Annotated[HandleFetchGoals, Depends(get_fetch_goals_use_case)]
DeleteGoalUseCaseDep = Annotated[HandleDeleteGoal, Depends(get_delete_goal_use_case)]
