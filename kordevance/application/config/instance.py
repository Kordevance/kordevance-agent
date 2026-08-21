from pathlib import Path

from kordevance.adapters.secret_store.file_secret import load_or_create_text
from kordevance.application import _WORKING_DIRECTORY
from kordevance.domain.security_utils import generate_short_token

_INSTANCE_ID_PATH: Path = _WORKING_DIRECTORY.joinpath("instance.id")


def load_or_create_instance_id() -> str:
    return load_or_create_text(_INSTANCE_ID_PATH, generate_short_token)
