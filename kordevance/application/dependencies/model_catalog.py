from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from kordevance.adapters.http.model_catalog_client import HttpModelCatalogClient
from kordevance.application.dependencies.sql_store_adapter import ModelProviderDep
from kordevance.domain.ports.model_catalog_client import ModelCatalogClient
from kordevance.domain.use_cases.llm_provider_management.handle_fetch_model_catalog import HandleFetchModelCatalog


@lru_cache(maxsize=1)
def get_model_catalog_client() -> ModelCatalogClient:
    return HttpModelCatalogClient()


def get_fetch_model_catalog_use_case(repository: ModelProviderDep) -> HandleFetchModelCatalog:
    return HandleFetchModelCatalog(repository=repository, catalog_client=get_model_catalog_client())


FetchModelCatalogUseCaseDep = Annotated[HandleFetchModelCatalog, Depends(get_fetch_model_catalog_use_case)]
