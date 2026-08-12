from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import col, delete, select, update
from sqlmodel.ext.asyncio.session import AsyncSession

from kordevance.adapters.sql_store.records.profile_record import ProfileRecord
from kordevance.domain.models.profile import Profile
from kordevance.domain.ports.profile_repository import ProfileRepo
from kordevance.exceptions import ProfileNotFoundError


class ProfileRepository(ProfileRepo):
    def __init__(self, db_context: AsyncEngine) -> None:
        self._engine: AsyncEngine = db_context

    async def save(self, name: str) -> Profile:
        record = ProfileRecord(name=name)
        async with AsyncSession(self._engine) as session:
            session.add(record)
            await session.commit()
            await session.refresh(record)

        return Profile(id=record.id, name=record.name)

    async def delete(self, profile_id: UUID) -> None:
        async with AsyncSession(self._engine) as session:
            result = await session.exec(delete(ProfileRecord).where(col(ProfileRecord.id) == profile_id))
            await session.commit()

            if result.rowcount == 0:
                raise ProfileNotFoundError(f"Could not find any profile with ID: {profile_id}")

    async def fetch(self, profile_id: UUID) -> Profile:
        async with AsyncSession(self._engine) as session:
            row = (await session.exec(select(ProfileRecord).where(ProfileRecord.id == profile_id))).one_or_none()

            if row is None:
                raise ProfileNotFoundError(f"Could not find any profile with ID: {profile_id}")

            return Profile(id=row.id, name=row.name)

    async def fetch_all(self) -> list[Profile]:
        async with AsyncSession(self._engine) as session:
            rows = (await session.exec(select(ProfileRecord))).all()
            return [Profile(id=row.id, name=row.name) for row in rows]

    async def update(self, profile: Profile) -> None:
        async with AsyncSession(self._engine) as session:
            result = await session.exec(
                update(ProfileRecord).where(col(ProfileRecord.id) == profile.id).values(name=profile.name)
            )
            await session.commit()

            if result.rowcount == 0:
                raise ProfileNotFoundError(f"Could not find any profile with ID: {profile.id}")
