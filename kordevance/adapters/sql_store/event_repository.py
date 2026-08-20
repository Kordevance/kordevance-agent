from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import col, select, update
from sqlmodel.ext.asyncio.session import AsyncSession

from kordevance.adapters.sql_store.records.event_record import EventRecord
from kordevance.domain.models.event import Event
from kordevance.domain.ports.event_repository import EventRepo
from kordevance.exceptions import ItemNotFoundError


class EventRepository(EventRepo):
    def __init__(self, db_context: AsyncEngine) -> None:
        self._engine: AsyncEngine = db_context

    @staticmethod
    def _to_domain(row: EventRecord) -> Event:
        return Event(
            id=row.id,
            profile_id=row.profile_id,
            goal_id=row.goal_id,
            engine_source=row.engine_source,
            connector_provider=row.connector_provider,
            origin_signature=row.origin_signature,
            raw_content=row.raw_content,
            occurred_at=row.occurred_at,
            classified_type=row.classified_type,
            extracted_fields=row.extracted_fields,
            confidence=row.confidence,
            linked_task_id=row.linked_task_id,
            created_at=row.created_at,
        )

    async def save(self, event: Event) -> None:
        record = EventRecord(
            id=event.id,
            profile_id=event.profile_id,
            goal_id=event.goal_id,
            engine_source=event.engine_source,
            connector_provider=event.connector_provider,
            origin_signature=event.origin_signature,
            raw_content=event.raw_content,
            occurred_at=event.occurred_at,
            classified_type=event.classified_type,
            extracted_fields=event.extracted_fields,
            confidence=event.confidence,
            linked_task_id=event.linked_task_id,
            created_at=event.created_at,
        )

        async with AsyncSession(self._engine) as session:
            session.add(record)
            await session.commit()

    async def fetch(self, profile_id: UUID, event_id: UUID) -> Event:
        async with AsyncSession(self._engine) as session:
            row = (
                await session.exec(
                    select(EventRecord).where(
                        col(EventRecord.profile_id) == profile_id, col(EventRecord.id) == event_id
                    )
                )
            ).one_or_none()

            if row is None:
                raise ItemNotFoundError(f"Could not find an event with ID: {event_id}")

            return self._to_domain(row)

    async def fetch_all_for_goal(self, profile_id: UUID, goal_id: UUID) -> list[Event]:
        async with AsyncSession(self._engine) as session:
            rows = (
                await session.exec(
                    select(EventRecord).where(
                        col(EventRecord.profile_id) == profile_id, col(EventRecord.goal_id) == goal_id
                    )
                )
            ).all()

            return [self._to_domain(row) for row in rows]

    async def update(self, event: Event) -> None:
        async with AsyncSession(self._engine) as session:
            result = await session.exec(
                update(EventRecord)
                .where(col(EventRecord.profile_id) == event.profile_id, col(EventRecord.id) == event.id)
                .values(
                    goal_id=event.goal_id,
                    classified_type=event.classified_type,
                    extracted_fields=event.extracted_fields,
                    confidence=event.confidence,
                    linked_task_id=event.linked_task_id,
                )
            )
            await session.commit()

            if result.rowcount == 0:
                raise ItemNotFoundError(f"Could not find an event with ID: {event.id}")
