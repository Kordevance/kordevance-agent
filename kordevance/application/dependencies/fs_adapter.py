from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from kordevance.adapters.fs.jsonl_message_store import JsonlMessageStore
from kordevance.adapters.fs.local_profile_workspace import LocalProfileWorkspace
from kordevance.application import _WORKING_DIRECTORY
from kordevance.domain.ports.message_store import MessageStore
from kordevance.domain.ports.profile_workspace import ProfileWorkspace

_PROFILES_DIR = _WORKING_DIRECTORY.joinpath("profiles")


@lru_cache(maxsize=1)
def get_profile_workspace() -> ProfileWorkspace:
    return LocalProfileWorkspace(_PROFILES_DIR)


@lru_cache(maxsize=1)
def get_message_store() -> MessageStore:
    return JsonlMessageStore(get_profile_workspace())


ProfileWorkspaceDep = Annotated[ProfileWorkspace, Depends(get_profile_workspace)]
MessageStoreDep = Annotated[MessageStore, Depends(get_message_store)]
