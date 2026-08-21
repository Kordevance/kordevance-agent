from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from kordevance.adapters.sql_store.records.paired_device_record import PairedDeviceRecord
from kordevance.domain.models.paired_device import PairedDevice
from kordevance.domain.ports.paired_device_repository import PairedDeviceRepo
from kordevance.exceptions import ItemNotFoundError


class PairedDeviceRepository(PairedDeviceRepo):
    def __init__(self, db_context: AsyncEngine) -> None:
        self._engine: AsyncEngine = db_context

    async def exists_any(self) -> bool:
        async with AsyncSession(self._engine) as session:
            record = (await session.exec(select(PairedDeviceRecord.id).limit(1))).first()
            return record is not None

    async def create(self, token_hash: str, is_owner: bool) -> PairedDevice:
        async with AsyncSession(self._engine) as session:
            record = PairedDeviceRecord(token_hash=token_hash, is_owner=is_owner, created_at=datetime.now(UTC))
            session.add(record)
            await session.commit()
            await session.refresh(record)
            return PairedDevice(id=record.id, is_owner=record.is_owner, created_at=record.created_at)

    async def get_by_token_hash(self, token_hash: str) -> PairedDevice | None:
        async with AsyncSession(self._engine) as session:
            record = (
                await session.exec(select(PairedDeviceRecord).where(col(PairedDeviceRecord.token_hash) == token_hash))
            ).one_or_none()

            if record is None:
                return None

            return PairedDevice(id=record.id, is_owner=record.is_owner, created_at=record.created_at)

    async def fetch_all(self) -> list[PairedDevice]:
        async with AsyncSession(self._engine) as session:
            records = (await session.exec(select(PairedDeviceRecord))).all()
            return [PairedDevice(id=r.id, is_owner=r.is_owner, created_at=r.created_at) for r in records]

    async def set_owner(self, device_id: UUID, is_owner: bool) -> None:
        async with AsyncSession(self._engine) as session:
            record = (
                await session.exec(select(PairedDeviceRecord).where(col(PairedDeviceRecord.id) == device_id))
            ).one_or_none()

            if record is None:
                raise ItemNotFoundError(f"No paired device found: {device_id}")

            record.is_owner = is_owner
            session.add(record)
            await session.commit()
