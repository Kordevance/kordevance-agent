from kordevance.application.dependencies.fs_adapter import get_profile_workspace
from kordevance.application.dependencies.pairing import get_pairing_service
from kordevance.application.dependencies.sql_store_adapter import (
    get_event_repository,
    get_goal_repository,
    get_llm_provider_repository,
    get_model_assignment_repository,
    get_profile_repository,
    get_task_repository,
)
from kordevance.domain.use_cases.gateway_management.handle_factory_reset import HandleFactoryReset


def get_factory_reset_use_case() -> HandleFactoryReset:
    return HandleFactoryReset(
        pairing_service=get_pairing_service(),
        profile_repo=get_profile_repository(),
        llm_provider_repo=get_llm_provider_repository(),
        model_assignment_repo=get_model_assignment_repository(),
        goal_repo=get_goal_repository(),
        task_repo=get_task_repository(),
        event_repo=get_event_repository(),
        profile_workspace=get_profile_workspace(),
    )
