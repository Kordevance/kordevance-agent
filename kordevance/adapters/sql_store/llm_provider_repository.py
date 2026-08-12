from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import col, delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from kordevance.adapters.sql_store.records.llm_provider_record import LLMProviderRecord
from kordevance.domain.models.llm_provider import LLMProvider
from kordevance.domain.ports.llm_provider_repository import LLMProviderRepo
from kordevance.exceptions import ProviderNotFoundError


class LLMProviderRepository(LLMProviderRepo):
    def __init__(self, db_context: AsyncEngine) -> None:
        self._engine: AsyncEngine = db_context

    async def save(self, profile_id: UUID, provider: LLMProvider) -> None:
        record = LLMProviderRecord(
            id=provider.id,
            profile_id=profile_id,
            name=provider.name,
            endpoint=provider.endpoint,
            tokens_used=provider.tokens_used,
        )

        async with AsyncSession(self._engine) as session:
            session.add(record)
            await session.commit()
            await session.refresh(record)

    async def delete(self, profile_id: UUID, provider_id: UUID) -> None:
        async with AsyncSession(self._engine) as session:
            result = await session.exec(
                delete(LLMProviderRecord).where(
                    col(LLMProviderRecord.id) == profile_id, col(LLMProviderRecord.profile_id) == provider_id
                )
            )
            await session.commit()

            if result.rowcount == 0:
                raise ProviderNotFoundError(f"Could not find a provider with ID: {provider_id}")

    async def fetch(self, profile_id: UUID, provider_id: UUID) -> LLMProvider:
        async with AsyncSession(self._engine) as session:
            row = (
                await session.exec(
                    select(LLMProviderRecord).where(
                        col(LLMProviderRecord.id) == profile_id, col(LLMProviderRecord.profile_id) == provider_id
                    )
                )
            ).one_or_none()

            if row is None:
                raise ProviderNotFoundError(f"Could not find a provider with ID: {provider_id}")

            return LLMProvider(id=row.id, name=row.name, endpoint=row.endpoint, tokens_used=row.tokens_used)

    async def fetch_all(self, profile_id: UUID) -> list[LLMProvider]:
        async with AsyncSession(self._engine) as session:
            rows = (
                await session.exec(
                    select(LLMProviderRecord).where(
                        col(LLMProviderRecord.id) == profile_id,
                    )
                )
            ).all()

            return [
                LLMProvider(id=row.id, name=row.name, endpoint=row.endpoint, tokens_used=row.tokens_used)
                for row in rows
            ]
