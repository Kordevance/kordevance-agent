from typing import Annotated

from fastapi import Depends

from kordevance.application.dependencies.fs_adapter import ProfileWorkspaceDep
from kordevance.application.dependencies.goal_management import DeleteGoalUseCaseDep
from kordevance.application.dependencies.sql_store_adapter import (
    GoalRepoDep,
    ModelAssignmentDep,
    ModelProviderDep,
    ProfileRepoDep,
)
from kordevance.domain.use_cases.profile_management.handle_create_profile import HandleCreateProfile
from kordevance.domain.use_cases.profile_management.handle_delete_profile import HandleDeleteProfile
from kordevance.domain.use_cases.profile_management.handle_fetch_profile import HandleFetchProfile
from kordevance.domain.use_cases.profile_management.handle_fetch_profiles import HandleFetchProfiles
from kordevance.domain.use_cases.profile_management.handle_update_profile import HandleUpdateProfile


def get_create_profile_use_case(repository: ProfileRepoDep, workspace: ProfileWorkspaceDep) -> HandleCreateProfile:
    return HandleCreateProfile(profile_repository=repository, workspace=workspace)


def get_delete_profile_use_case(
    repository: ProfileRepoDep,
    workspace: ProfileWorkspaceDep,
    goal_repository: GoalRepoDep,
    delete_goal_use_case: DeleteGoalUseCaseDep,
    llm_provider_repository: ModelProviderDep,
    model_assignment_repository: ModelAssignmentDep,
) -> HandleDeleteProfile:
    return HandleDeleteProfile(
        profile_repository=repository,
        workspace=workspace,
        goal_repository=goal_repository,
        delete_goal_use_case=delete_goal_use_case,
        llm_provider_repository=llm_provider_repository,
        model_assignment_repository=model_assignment_repository,
    )


def get_update_profile_use_case(repository: ProfileRepoDep) -> HandleUpdateProfile:
    return HandleUpdateProfile(profile_repository=repository)


def get_fetch_profile_use_case(repository: ProfileRepoDep) -> HandleFetchProfile:
    return HandleFetchProfile(profile_repository=repository)


def get_fetch_profiles_use_case(repository: ProfileRepoDep) -> HandleFetchProfiles:
    return HandleFetchProfiles(profile_repository=repository)


CreateProfileUseCaseDep = Annotated[HandleCreateProfile, Depends(get_create_profile_use_case)]
UpdateProfileUseCaseDep = Annotated[HandleUpdateProfile, Depends(get_update_profile_use_case)]
DeleteProfileUseCaseDep = Annotated[HandleDeleteProfile, Depends(get_delete_profile_use_case)]
GetProfileUseCaseDep = Annotated[HandleFetchProfile, Depends(get_fetch_profile_use_case)]
GetProfilesUseCaseDep = Annotated[HandleFetchProfiles, Depends(get_fetch_profiles_use_case)]
