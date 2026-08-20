from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import col, delete, select, update
from sqlmodel.ext.asyncio.session import AsyncSession

from kordevance.adapters.sql_store.records.goal_record import GoalRecord
from kordevance.domain.models.connectors import Connector
from kordevance.domain.models.goal import Goal
from kordevance.domain.ports.goal_repository import GoalRepo
from kordevance.exceptions import ItemNotFoundError


class GoalRepository(GoalRepo):
    def __init__(self, db_context: AsyncEngine) -> None:
        self._engine: AsyncEngine = db_context

    @staticmethod
    def _to_domain(row: GoalRecord) -> Goal:
        return Goal(
            id=row.id,
            profile_id=row.profile_id,
            title=row.title,
            description=row.description,
            domain=row.domain,
            status=row.status,
            start_at=row.start_at,
            end_at=row.end_at,
            horizon_granularity=row.horizon_granularity,
            due_date=row.due_date,
            progress_metric_type=row.progress_metric_type,
            target_value=row.target_value,
            current_value=row.current_value,
            required_connectors=[Connector(**connector) for connector in row.required_connectors],
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    async def save(self, goal: Goal) -> None:
        record = GoalRecord(
            id=goal.id,
            profile_id=goal.profile_id,
            title=goal.title,
            description=goal.description,
            domain=goal.domain,
            status=goal.status,
            start_at=goal.start_at,
            end_at=goal.end_at,
            horizon_granularity=goal.horizon_granularity,
            due_date=goal.due_date,
            progress_metric_type=goal.progress_metric_type,
            target_value=goal.target_value,
            current_value=goal.current_value,
            required_connectors=[connector.model_dump() for connector in goal.required_connectors],
            created_at=goal.created_at,
            updated_at=goal.updated_at,
        )

        async with AsyncSession(self._engine) as session:
            session.add(record)
            await session.commit()

    async def fetch(self, profile_id: UUID, goal_id: UUID) -> Goal:
        async with AsyncSession(self._engine) as session:
            row = (
                await session.exec(
                    select(GoalRecord).where(col(GoalRecord.profile_id) == profile_id, col(GoalRecord.id) == goal_id)
                )
            ).one_or_none()

            if row is None:
                raise ItemNotFoundError(f"Could not find a goal with ID: {goal_id}")

            return self._to_domain(row)

    async def fetch_all(self, profile_id: UUID) -> list[Goal]:
        async with AsyncSession(self._engine) as session:
            rows = (await session.exec(select(GoalRecord).where(col(GoalRecord.profile_id) == profile_id))).all()

            return [self._to_domain(row) for row in rows]

    async def update(self, goal: Goal) -> None:
        async with AsyncSession(self._engine) as session:
            result = await session.exec(
                update(GoalRecord)
                .where(col(GoalRecord.profile_id) == goal.profile_id, col(GoalRecord.id) == goal.id)
                .values(
                    title=goal.title,
                    description=goal.description,
                    domain=goal.domain,
                    status=goal.status,
                    start_at=goal.start_at,
                    end_at=goal.end_at,
                    horizon_granularity=goal.horizon_granularity,
                    due_date=goal.due_date,
                    progress_metric_type=goal.progress_metric_type,
                    target_value=goal.target_value,
                    current_value=goal.current_value,
                    required_connectors=[connector.model_dump() for connector in goal.required_connectors],
                    updated_at=goal.updated_at,
                )
            )
            await session.commit()

            if result.rowcount == 0:
                raise ItemNotFoundError(f"Could not find a goal with ID: {goal.id}")

    async def delete(self, profile_id: UUID, goal_id: UUID) -> None:
        async with AsyncSession(self._engine) as session:
            result = await session.exec(
                delete(GoalRecord).where(col(GoalRecord.profile_id) == profile_id, col(GoalRecord.id) == goal_id)
            )
            await session.commit()

            if result.rowcount == 0:
                raise ItemNotFoundError(f"Could not find a goal with ID: {goal_id}")
