from abc import ABC, abstractmethod
from typing import Generic, TypeVar

TInput = TypeVar("TInput")
TOutput = TypeVar("TOutput")


class UseCase(ABC, Generic[TInput, TOutput]):
    @abstractmethod
    async def execute(self, request: TInput) -> TOutput:
        raise NotImplementedError
