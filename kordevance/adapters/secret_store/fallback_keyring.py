import logging

import keyring
from keyring.backend import KeyringBackend
from keyring.backends.kwallet import DBusKeyring as KWalletKeyring
from keyring.backends.libsecret import Keyring as LibSecretKeyring
from keyring.backends.macOS import Keyring as MacOSKeyring
from keyring.backends.SecretService import Keyring as SecretServiceKeyring
from keyring.backends.Windows import WinVaultKeyring
from keyrings.cryptfile.cryptfile import CryptFileKeyring

from kordevance.adapters.secret_store.file_secret import load_or_create_text
from kordevance.application import _WORKING_DIRECTORY
from kordevance.domain.security_utils import generate_device_token

_TRUSTED_BACKENDS: tuple[type[KeyringBackend], ...] = (
    MacOSKeyring,
    WinVaultKeyring,
    SecretServiceKeyring,
    LibSecretKeyring,
    KWalletKeyring,
)

_KEYRING_KEY_PATH = _WORKING_DIRECTORY.joinpath("keyring.key")
_KEYRING_FILE_PATH = _WORKING_DIRECTORY.joinpath("credentials.cfg")


def ensure_usable_keyring() -> None:
    if isinstance(keyring.get_keyring(), _TRUSTED_BACKENDS):
        return

    logging.getLogger(__name__).warning(
        "No trusted OS keyring backend detected, falling back to an encrypted local credential store at %s",
        _KEYRING_FILE_PATH,
    )

    fallback = CryptFileKeyring()
    fallback.file_path = str(_KEYRING_FILE_PATH)
    fallback.keyring_key = load_or_create_text(_KEYRING_KEY_PATH, generate_device_token)

    keyring.set_keyring(fallback)
