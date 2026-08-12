from typing import Annotated

from fastapi import Depends

from kordevance.application.dependencies.sql_store_adapter import ProfileRepoDep
from kordevance.domain.use_cases.profile_management.handle_create_profile import HandleCreateProfile
from kordevance.domain.use_cases.profile_management.handle_delete_profile import HandleDeleteProfile
from kordevance.domain.use_cases.profile_management.handle_fetch_profile import HandleFetchProfile
from kordevance.domain.use_cases.profile_management.handle_fetch_profiles import HandleFetchProfiles
from kordevance.domain.use_cases.profile_management.handle_update_profile import HandleUpdateProfile


def get_create_profile_use_case(repository: ProfileRepoDep) -> HandleCreateProfile:
    return HandleCreateProfile(profile_repository=repository)


def get_delete_profile_use_case(repository: ProfileRepoDep) -> HandleDeleteProfile:
    return HandleDeleteProfile(profile_repository=repository)


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
