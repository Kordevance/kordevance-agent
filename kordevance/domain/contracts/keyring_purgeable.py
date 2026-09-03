from abc import ABC, abstractmethod


class KeyringPurgeable(ABC):
    @abstractmethod
    def purge_keyring(self) -> None: ...
