from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import col, delete, select, update
from sqlmodel.ext.asyncio.session import AsyncSession

from kordevance.adapters.sql_store.records.task_record import TaskRecord
from kordevance.domain.models.task import Task
from kordevance.domain.ports.task_repository import TaskRepo
from kordevance.exceptions import ItemNotFoundError


class TaskRepository(TaskRepo):
    def __init__(self, db_context: AsyncEngine) -> None:
        self._engine: AsyncEngine = db_context

    @staticmethod
    def _to_domain(row: TaskRecord) -> Task:
        return Task(
            id=row.id,
            profile_id=row.profile_id,
            goal_id=row.goal_id,
            title=row.title,
            description=row.description,
            due_date=row.due_date,
            status=row.status,
            status_confidence=row.status_confidence,
            source_type=row.source_type,
            provenance_event_id=row.provenance_event_id,
            external_actions=row.external_actions,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    async def save(self, task: Task) -> None:
        record = TaskRecord(
            id=task.id,
            profile_id=task.profile_id,
            goal_id=task.goal_id,
            title=task.title,
            description=task.description,
            due_date=task.due_date,
            status=task.status,
            status_confidence=task.status_confidence,
            source_type=task.source_type,
            provenance_event_id=task.provenance_event_id,
            external_actions=task.external_actions,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )

        async with AsyncSession(self._engine) as session:
            session.add(record)
            await session.commit()

    async def fetch(self, profile_id: UUID, task_id: UUID) -> Task:
        async with AsyncSession(self._engine) as session:
            row = (
                await session.exec(
                    select(TaskRecord).where(col(TaskRecord.profile_id) == profile_id, col(TaskRecord.id) == task_id)
                )
            ).one_or_none()

            if row is None:
                raise ItemNotFoundError(f"Could not find a task with ID: {task_id}")

            return self._to_domain(row)

    async def fetch_all_for_goal(self, profile_id: UUID, goal_id: UUID) -> list[Task]:
        async with AsyncSession(self._engine) as session:
            rows = (
                await session.exec(
                    select(TaskRecord).where(
                        col(TaskRecord.profile_id) == profile_id, col(TaskRecord.goal_id) == goal_id
                    )
                )
            ).all()

            return [self._to_domain(row) for row in rows]

    async def update(self, task: Task) -> None:
        async with AsyncSession(self._engine) as session:
            result = await session.exec(
                update(TaskRecord)
                .where(col(TaskRecord.profile_id) == task.profile_id, col(TaskRecord.id) == task.id)
                .values(
                    goal_id=task.goal_id,
                    title=task.title,
                    description=task.description,
                    due_date=task.due_date,
                    status=task.status,
                    status_confidence=task.status_confidence,
                    source_type=task.source_type,
                    provenance_event_id=task.provenance_event_id,
                    external_actions=task.external_actions,
                    updated_at=task.updated_at,
                )
            )
            await session.commit()

            if result.rowcount == 0:
                raise ItemNotFoundError(f"Could not find a task with ID: {task.id}")

    async def delete(self, profile_id: UUID, task_id: UUID) -> None:
        async with AsyncSession(self._engine) as session:
            result = await session.exec(
                delete(TaskRecord).where(col(TaskRecord.profile_id) == profile_id, col(TaskRecord.id) == task_id)
            )
            await session.commit()

            if result.rowcount == 0:
                raise ItemNotFoundError(f"Could not find a task with ID: {task_id}")

    async def delete_all_for_goal(self, profile_id: UUID, goal_id: UUID) -> None:
        async with AsyncSession(self._engine) as session:
            await session.exec(
                delete(TaskRecord).where(col(TaskRecord.profile_id) == profile_id, col(TaskRecord.goal_id) == goal_id)
            )
            await session.commit()

    async def delete_all(self) -> None:
        async with AsyncSession(self._engine) as session:
            await session.exec(delete(TaskRecord))
            await session.commit()
