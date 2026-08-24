from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import col, delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from kordevance.adapters.sql_store.records.pairing_invite_record import PairingInviteRecord
from kordevance.domain.models.pairing_invite import PairingInvite
from kordevance.domain.ports.pairing_invite_repository import PairingInviteRepo


class PairingInviteRepository(PairingInviteRepo):
    def __init__(self, db_context: AsyncEngine) -> None:
        self._engine: AsyncEngine = db_context

    async def create(self, code_hash: str, expires_at: datetime) -> None:
        async with AsyncSession(self._engine) as session:
            session.add(PairingInviteRecord(code_hash=code_hash, expires_at=expires_at, created_at=datetime.now(UTC)))
            await session.commit()

    async def fetch_live(self) -> list[PairingInvite]:
        async with AsyncSession(self._engine) as session:
            now = datetime.now(UTC).replace(tzinfo=None)
            records = (
                await session.exec(select(PairingInviteRecord).where(col(PairingInviteRecord.expires_at) > now))
            ).all()
            return [
                PairingInvite(id=r.id, code_hash=r.code_hash, expires_at=r.expires_at, created_at=r.created_at)
                for r in records
            ]

    async def delete(self, invite_id: UUID) -> None:
        async with AsyncSession(self._engine) as session:
            await session.exec(delete(PairingInviteRecord).where(col(PairingInviteRecord.id) == invite_id))
            await session.commit()

    async def delete_all(self) -> None:
        async with AsyncSession(self._engine) as session:
            await session.exec(delete(PairingInviteRecord))
            await session.commit()
