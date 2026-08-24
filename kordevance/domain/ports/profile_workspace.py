from abc import ABC, abstractmethod
from pathlib import Path
from uuid import UUID


class ProfileWorkspace(ABC):
    @abstractmethod
    async def create_profile(self, profile_id: UUID) -> Path:
        """Create the profile's workspace directory and return its path."""
        ...

    @abstractmethod
    async def delete_profile(self, profile_id: UUID) -> None:
        """Remove the profile's workspace directory and everything under it."""
        ...

    @abstractmethod
    async def load_profile(self, profile_id: UUID) -> Path:
        """Return the profile's workspace directory, ensuring it exists first."""
        ...

    @abstractmethod
    async def delete_all(self) -> None:
        """Remove every profile's workspace directory and everything under it."""
        ...
