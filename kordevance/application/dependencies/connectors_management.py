from typing import Annotated

from fastapi import Depends

from kordevance.application.dependencies.proxy_relay_client import get_proxy_relay_client
from kordevance.application.dependencies.secret_store_adapter import get_credential_manager
from kordevance.domain.use_cases.connectors_management.handle_fetch_connectors import HandleFetchConnectors


def get_fetch_connectors_use_case() -> HandleFetchConnectors:
    return HandleFetchConnectors(
        credential_manager=get_credential_manager(),
        proxy_relay_client=get_proxy_relay_client(),
    )


FetchConnectorsUseCaseDep = Annotated[HandleFetchConnectors, Depends(get_fetch_connectors_use_case)]
