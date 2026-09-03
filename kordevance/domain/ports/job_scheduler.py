from abc import ABC, abstractmethod
from uuid import UUID

DEFAULT_CYCLE_INTERVAL_SECONDS = 2 * 60 * 60  # 2 Hours


class JobScheduler(ABC):
    @abstractmethod
    def start(self) -> None: ...
    @abstractmethod
    def shutdown(self) -> None: ...
    @abstractmethod
    def schedule_goal_cycle(self, profile_id: UUID, goal_id: UUID, interval_seconds: int) -> None: ...
    @abstractmethod
    def unschedule_goal_cycle(self, goal_id: UUID) -> None: ...
