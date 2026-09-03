from abc import ABC, abstractmethod
from uuid import UUID

from kordevance.domain.models.model_assignment import ModelAssignment
from kordevance.domain.models.model_role import ModelRole


class ModelAssignmentRepo(ABC):
    @abstractmethod
    async def save(self, profile_id: UUID, assignment: ModelAssignment) -> None:
        """Create or replace the assignment for (profile_id, assignment.role)."""
        ...

    @abstractmethod
    async def delete(self, profile_id: UUID, role: ModelRole) -> None: ...
    @abstractmethod
    async def fetch(self, profile_id: UUID, role: ModelRole) -> ModelAssignment: ...
    @abstractmethod
    async def fetch_all(self, profile_id: UUID) -> list[ModelAssignment]: ...
    @abstractmethod
    async def delete_all(self) -> None: ...
