from typing import Annotated

from fastapi import Depends

from kordevance.application import _APPLICATION_NAME
from kordevance.domain.ports.credential_manager import CredManager
from kordevance.adapters.secret_store.credential_manager import CredentialManager


def get_credential_manager() -> CredManager:
    return CredentialManager(tag=_APPLICATION_NAME)


CredManagerDep = Annotated[CredManager, Depends(get_credential_manager)]
