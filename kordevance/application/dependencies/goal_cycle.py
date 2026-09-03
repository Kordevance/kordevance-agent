from typing import Annotated

from fastapi import Depends

from kordevance.adapters.agents.engines.goal_cycle_engine import PydanticAIGoalCycleEngine
from kordevance.adapters.agents.model_resolver import ModelResolver
from kordevance.application.dependencies.proxy_relay_client import get_proxy_relay_client
from kordevance.application.dependencies.secret_store_adapter import get_credential_manager
from kordevance.application.dependencies.sql_store_adapter import (
    EventRepoDep,
    GoalRepoDep,
    ModelAssignmentDep,
    ModelProviderDep,
    ProfileRepoDep,
    TaskRepoDep,
    get_llm_provider_repository,
    get_model_assignment_repository,
)
from kordevance.domain.ports.goal_cycle_engine import GoalCycleEngine
from kordevance.domain.services.device_service import DeviceService
from kordevance.domain.use_cases.goal_cycle_management.handle_run_goal_cycle import HandleRunGoalCycle


def _get_model_resolver(
    model_assignment_repo: ModelAssignmentDep, llm_provider_repo: ModelProviderDep
) -> ModelResolver:
    return ModelResolver(model_assignment_repo=model_assignment_repo, llm_provider_repo=llm_provider_repo)


def _get_device_service() -> DeviceService:
    return DeviceService(store=get_credential_manager())


def get_goal_cycle_engine(
    model_resolver: Annotated[ModelResolver, Depends(_get_model_resolver)],
) -> GoalCycleEngine:
    return PydanticAIGoalCycleEngine(
        model_resolver=model_resolver,
        proxy_relay_client=get_proxy_relay_client(),
        device_service=_get_device_service(),
    )


def get_goal_cycle_engine_standalone() -> GoalCycleEngine:
    """Same construction as get_goal_cycle_engine, but outside FastAPI's Depends (tailored for the
    scheduler job, which runs on APScheduler's own loop rather than inside a request.)"""
    model_resolver = _get_model_resolver(
        model_assignment_repo=get_model_assignment_repository(), llm_provider_repo=get_llm_provider_repository()
    )
    return PydanticAIGoalCycleEngine(
        model_resolver=model_resolver,
        proxy_relay_client=get_proxy_relay_client(),
        device_service=_get_device_service(),
    )


def get_run_goal_cycle_use_case(
    goal_repo: GoalRepoDep,
    task_repo: TaskRepoDep,
    event_repo: EventRepoDep,
    goal_cycle_engine: Annotated[GoalCycleEngine, Depends(get_goal_cycle_engine)],
    profile_repo: ProfileRepoDep,
) -> HandleRunGoalCycle:
    return HandleRunGoalCycle(
        goal_repo=goal_repo,
        task_repo=task_repo,
        event_repo=event_repo,
        goal_cycle_engine=goal_cycle_engine,
        profile_repo=profile_repo,
    )


RunGoalCycleUseCaseDep = Annotated[HandleRunGoalCycle, Depends(get_run_goal_cycle_use_case)]
