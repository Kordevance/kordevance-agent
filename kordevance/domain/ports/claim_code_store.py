from abc import ABC, abstractmethod


class ClaimCodeStore(ABC):
    @abstractmethod
    def get_or_create(self) -> str: ...
    @abstractmethod
    def invalidate(self) -> None: ...
    @abstractmethod
    def peek(self) -> str | None: ...
