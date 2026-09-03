from abc import ABC, abstractmethod


class CredManager(ABC):
    @abstractmethod
    def get(self, service: str, key: str) -> str | None: ...
    @abstractmethod
    def set(self, service: str, key: str, value: str) -> None: ...
    @abstractmethod
    def delete(self, service: str, key: str) -> None: ...
