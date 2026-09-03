from cryptography.fernet import Fernet

from kordevance.domain.contracts.keyring_purgeable import KeyringPurgeable
from kordevance.domain.ports.credential_manager import CredManager


class KeyringMasterKey(KeyringPurgeable):
    def __init__(self, store: CredManager) -> None:
        self._store: CredManager = store

        self.__SERVICE: str = "encryption"
        self.__KEY: str = "master_key"

    def load_or_create(self) -> bytes:
        value = self._store.get(self.__SERVICE, self.__KEY)
        if value is not None:
            return value.encode("utf-8")

        key = Fernet.generate_key()
        self._store.set(self.__SERVICE, self.__KEY, key.decode("utf-8"))
        return key

    def purge_keyring(self) -> None:
        self._store.delete(self.__SERVICE, self.__KEY)
