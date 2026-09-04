import logging

import keyring
from keyring.backends.fail import Keyring as FailKeyring
from keyrings.cryptfile.cryptfile import CryptFileKeyring

from kordevance.adapters.secret_store.file_secret import load_or_create_text
from kordevance.application import _WORKING_DIRECTORY
from kordevance.domain.security_utils import generate_device_token

_KEYRING_KEY_PATH = _WORKING_DIRECTORY.joinpath("keyring.key")
_KEYRING_FILE_PATH = _WORKING_DIRECTORY.joinpath("credentials.cfg")


def ensure_usable_keyring() -> None:
    if not isinstance(keyring.get_keyring(), FailKeyring):
        return

    logging.getLogger(__name__).warning(
        "No OS keyring backend detected, falling back to an encrypted local credential store at %s",
        _KEYRING_FILE_PATH,
    )

    fallback = CryptFileKeyring()
    fallback.file_path = str(_KEYRING_FILE_PATH)
    fallback.keyring_key = load_or_create_text(_KEYRING_KEY_PATH, generate_device_token)

    keyring.set_keyring(fallback)
