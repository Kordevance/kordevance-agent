from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from kordevance import _APPLICATION_NAME
from kordevance.adapters.secret_store.credential_manager import CredentialManager
from kordevance.application.config.instance import load_or_create_instance_id
from kordevance.domain.ports.credential_manager import CredManager


@lru_cache(maxsize=1)
def get_credential_manager() -> CredManager:
    return CredentialManager(tag=f"{_APPLICATION_NAME}:{load_or_create_instance_id()}")


CredManagerDep = Annotated[CredManager, Depends(get_credential_manager)]
