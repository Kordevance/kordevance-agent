from pathlib import Path

from cryptography.fernet import Fernet

from kordevance.adapters.secret_store.file_secret import load_or_create_bytes
from kordevance.application import _WORKING_DIRECTORY

_KEY_PATH: Path = _WORKING_DIRECTORY.joinpath("secret.key")


def load_or_create_encryption_key() -> bytes:
    return load_or_create_bytes(_KEY_PATH, Fernet.generate_key)
