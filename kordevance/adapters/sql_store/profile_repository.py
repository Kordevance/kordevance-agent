from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import col, delete, select, update
from sqlmodel.ext.asyncio.session import AsyncSession

from kordevance.adapters.sql_store.records.profile_record import ProfileRecord
from kordevance.domain.models.profile import Profile
from kordevance.domain.ports.profile_repository import ProfileRepo
from kordevance.exceptions import ItemNotFoundError


class ProfileRepository(ProfileRepo):
    def __init__(self, db_context: AsyncEngine) -> None:
        self._engine: AsyncEngine = db_context

    async def save(self, name: str, home_timezone: str, last_known_timezone: str) -> Profile:
        record = ProfileRecord(
            name=name,
            home_timezone=home_timezone,
            last_known_timezone=last_known_timezone,
            last_timezone_sync_at=datetime.now(),
        )
        async with AsyncSession(self._engine) as session:
            session.add(record)
            await session.commit()
            await session.refresh(record)

        return Profile(
            id=record.id,
            name=record.name,
            home_timezone=record.home_timezone,
            last_known_timezone=record.last_known_timezone,
            last_timezone_sync_at=record.last_timezone_sync_at,
        )

    async def delete(self, profile_id: UUID) -> None:
        async with AsyncSession(self._engine) as session:
            result = await session.exec(delete(ProfileRecord).where(col(ProfileRecord.id) == profile_id))
            await session.commit()

            if result.rowcount == 0:
                raise ItemNotFoundError(f"Could not find any profile with ID: {profile_id}")

    async def fetch(self, profile_id: UUID) -> Profile:
        async with AsyncSession(self._engine) as session:
            row = (await session.exec(select(ProfileRecord).where(ProfileRecord.id == profile_id))).one_or_none()

            if row is None:
                raise ItemNotFoundError(f"Could not find any profile with ID: {profile_id}")

            return Profile(
                id=row.id,
                name=row.name,
                home_timezone=row.home_timezone,
                last_known_timezone=row.last_known_timezone,
                last_timezone_sync_at=row.last_timezone_sync_at,
            )

    async def fetch_all(self) -> list[Profile]:
        async with AsyncSession(self._engine) as session:
            rows = (await session.exec(select(ProfileRecord))).all()
            return [
                Profile(
                    id=row.id,
                    name=row.name,
                    home_timezone=row.home_timezone,
                    last_known_timezone=row.last_known_timezone,
                    last_timezone_sync_at=row.last_timezone_sync_at,
                )
                for row in rows
            ]

    async def update(self, profile: Profile) -> None:
        async with AsyncSession(self._engine) as session:
            result = await session.exec(
                update(ProfileRecord)
                .where(col(ProfileRecord.id) == profile.id)
                .values(name=profile.name, home_timezone=profile.home_timezone)
            )
            await session.commit()

            if result.rowcount == 0:
                raise ItemNotFoundError(f"Could not find any profile with ID: {profile.id}")

    async def delete_all(self) -> None:
        async with AsyncSession(self._engine) as session:
            await session.exec(delete(ProfileRecord))
            await session.commit()

    async def update_timezone(self, profile_id: UUID, timezone: str) -> None:
        async with AsyncSession(self._engine) as session:
            statement = (
                update(ProfileRecord)
                .where(col(ProfileRecord.id) == profile_id, col(ProfileRecord.last_known_timezone) != timezone)
                .values(
                    last_known_timezone=timezone,
                    last_timezone_sync_at=datetime.now(),
                )
            )
            await session.exec(statement)
            await session.commit()

    async def fetch_timezone(self, profile_id: UUID) -> str | None:
        async with AsyncSession(self._engine) as session:
            row = (await session.exec(select(ProfileRecord).where(col(ProfileRecord.id) == profile_id))).one_or_none()

            if row is None:
                return None

            return row.last_known_timezone
