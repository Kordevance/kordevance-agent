from typing import Annotated

from fastapi import Depends

from kordevance.application.dependencies.proxy_relay_client import get_proxy_relay_client
from kordevance.application.dependencies.secret_store_adapter import get_credential_manager
from kordevance.domain.use_cases.connectors_management.handle_delete_connector import HandleDeleteConnector
from kordevance.domain.use_cases.connectors_management.handle_fetch_connectors import HandleFetchConnectors
from kordevance.domain.use_cases.connectors_management.handle_register_connector import HandleRegisterConnector


def get_fetch_connectors_use_case() -> HandleFetchConnectors:
    return HandleFetchConnectors(
        credential_manager=get_credential_manager(),
        proxy_relay_client=get_proxy_relay_client(),
    )


def get_register_connector_use_case() -> HandleRegisterConnector:
    return HandleRegisterConnector(
        credential_manager=get_credential_manager(),
        proxy_relay_client=get_proxy_relay_client(),
    )


def get_delete_connector_use_case() -> HandleDeleteConnector:
    return HandleDeleteConnector(
        credential_manager=get_credential_manager(),
        proxy_relay_client=get_proxy_relay_client(),
    )


FetchConnectorsUseCaseDep = Annotated[HandleFetchConnectors, Depends(get_fetch_connectors_use_case)]
RegisterConnectorsUseCaseDep = Annotated[HandleRegisterConnector, Depends(get_register_connector_use_case)]
DeleteConnectorsUseCaseDep = Annotated[HandleDeleteConnector, Depends(get_delete_connector_use_case)]
