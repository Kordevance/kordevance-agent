from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import col, delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from kordevance.adapters.sql_store.records.model_assignment_record import ModelAssignmentRecord
from kordevance.domain.models.model_assignment import ModelAssignment
from kordevance.domain.models.model_role import ModelRole
from kordevance.domain.ports.model_assignment_repository import ModelAssignmentRepo
from kordevance.exceptions import ItemNotFoundError


class ModelAssignmentRepository(ModelAssignmentRepo):
    def __init__(self, db_context: AsyncEngine) -> None:
        self._engine: AsyncEngine = db_context

    async def save(self, profile_id: UUID, assignment: ModelAssignment) -> None:
        async with AsyncSession(self._engine) as session:
            existing = (
                await session.exec(
                    select(ModelAssignmentRecord).where(
                        col(ModelAssignmentRecord.profile_id) == profile_id,
                        col(ModelAssignmentRecord.role) == assignment.role,
                    )
                )
            ).one_or_none()

            if existing is None:
                session.add(
                    ModelAssignmentRecord(
                        profile_id=profile_id,
                        role=assignment.role,
                        provider_id=assignment.provider_id,
                        model_id=assignment.model_id,
                    )
                )
            else:
                existing.provider_id = assignment.provider_id
                existing.model_id = assignment.model_id
                session.add(existing)

            await session.commit()

    async def delete(self, profile_id: UUID, role: ModelRole) -> None:
        async with AsyncSession(self._engine) as session:
            result = await session.exec(
                delete(ModelAssignmentRecord).where(
                    col(ModelAssignmentRecord.profile_id) == profile_id, col(ModelAssignmentRecord.role) == role
                )
            )
            await session.commit()

            if result.rowcount == 0:
                raise ItemNotFoundError(f"No {role} model assignment found for profile: {profile_id}")

    async def fetch_all(self, profile_id: UUID) -> list[ModelAssignment]:
        async with AsyncSession(self._engine) as session:
            rows = (
                await session.exec(
                    select(ModelAssignmentRecord).where(col(ModelAssignmentRecord.profile_id) == profile_id)
                )
            ).all()

            return [ModelAssignment(role=row.role, provider_id=row.provider_id, model_id=row.model_id) for row in rows]
