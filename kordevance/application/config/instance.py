import secrets
from pathlib import Path

from kordevance.application import _WORKING_DIRECTORY

_INSTANCE_ID_PATH: Path = _WORKING_DIRECTORY.joinpath("instance.id")


def load_or_create_instance_id() -> str:
    if _INSTANCE_ID_PATH.exists():
        return _INSTANCE_ID_PATH.read_text().strip()

    instance_id = secrets.token_hex(8)
    _INSTANCE_ID_PATH.write_text(instance_id)
    _INSTANCE_ID_PATH.chmod(0o600)
    return instance_id
