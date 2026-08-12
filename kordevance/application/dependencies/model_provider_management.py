from typing import Annotated

from fastapi import Depends

from kordevance.application.dependencies.sql_store_adapter import ModelProviderDep
from kordevance.domain.use_cases.llm_provider_management.handle_add_provider import HandleAddProvider
from kordevance.domain.use_cases.llm_provider_management.handle_delete_provider import HandleDeleteProvider
from kordevance.domain.use_cases.llm_provider_management.handle_fetch_provider import HandleFetchProvider
from kordevance.domain.use_cases.llm_provider_management.handle_fetch_providers import HandleFetchProviders


def get_add_provider_use_case(repository: ModelProviderDep) -> HandleAddProvider:
    return HandleAddProvider(repository=repository)


def get_delete_provider_use_case(repository: ModelProviderDep) -> HandleDeleteProvider:
    return HandleDeleteProvider(repository=repository)


def get_fetch_provider_use_case(repository: ModelProviderDep) -> HandleFetchProvider:
    return HandleFetchProvider(repository=repository)


def get_fetch_providers_use_case(repository: ModelProviderDep) -> HandleFetchProviders:
    return HandleFetchProviders(repository=repository)


AddProviderUseCaseDep = Annotated[HandleAddProvider, Depends(get_add_provider_use_case)]
DeleteProviderUseCaseDep = Annotated[HandleDeleteProvider, Depends(get_delete_provider_use_case)]
GetProviderUseCaseDep = Annotated[HandleFetchProvider, Depends(get_fetch_provider_use_case)]
GetProvidersUseCaseDep = Annotated[HandleFetchProviders, Depends(get_fetch_providers_use_case)]
