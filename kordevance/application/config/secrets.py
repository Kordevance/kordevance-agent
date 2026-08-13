from pathlib import Path

from cryptography.fernet import Fernet

from kordevance.application import _WORKING_DIRECTORY

_KEY_PATH: Path = _WORKING_DIRECTORY.joinpath("secret.key")


def load_or_create_encryption_key() -> bytes:
    """Load the local Fernet key used to encrypt provider API keys at rest, generating one on first run.

    The key lives in the process' working directory
    """
    if _KEY_PATH.exists():
        return _KEY_PATH.read_bytes()

    key = Fernet.generate_key()
    _KEY_PATH.write_bytes(key)
    _KEY_PATH.chmod(0o600)
    return key
