from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from kordevance.adapters.sql_store.records.device_registration_record import DeviceRegistrationRecord
from kordevance.domain.models.device_registration import DeviceRegistration
from kordevance.domain.ports.device_registration_repository import DeviceRegistrationRepo

_SINGLETON_ID: int = 1


class DeviceRegistrationRepository(DeviceRegistrationRepo):
    def __init__(self, db_context: AsyncEngine) -> None:
        self._engine: AsyncEngine = db_context

    async def get(self) -> DeviceRegistration | None:
        async with AsyncSession(self._engine) as session:
            record = (
                await session.exec(
                    select(DeviceRegistrationRecord).where(col(DeviceRegistrationRecord.id) == _SINGLETON_ID)
                )
            ).one_or_none()

            if record is None:
                return None

            return DeviceRegistration(device_id=record.device_id, registered_at=record.registered_at)

    async def save(self, device_id: str) -> None:
        async with AsyncSession(self._engine) as session:
            session.add(
                DeviceRegistrationRecord(id=_SINGLETON_ID, device_id=device_id, registered_at=datetime.now(UTC))
            )
            await session.commit()
