import keyring
from keyring.errors import PasswordDeleteError

from kordevance.domain.ports.credential_manager import CredManager


class CredentialManager(CredManager):
    def __init__(self, tag: str) -> None:
        self._tag: str = tag

    def _namespaced_service(self, service: str) -> str:
        return f"{self._tag}:{service}"

    def get(self, service: str, key: str) -> str | None:
        return keyring.get_password(self._namespaced_service(service), key)

    def set(self, service: str, key: str, value: str) -> None:
        keyring.set_password(self._namespaced_service(service), key, value)

    def delete(self, service: str, key: str) -> None:
        try:
            keyring.delete_password(self._namespaced_service(service), key)
        except PasswordDeleteError:
            # no-op if the credential doesn't exist
            pass
