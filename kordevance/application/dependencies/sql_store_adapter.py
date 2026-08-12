from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import SQLModel

from kordevance.adapters.sql_store.profile_repository import ProfileRepository
from kordevance.application import _WORKING_DIRECTORY
from kordevance.domain.ports.profile_repository import ProfileRepo

_DB_PATH = _WORKING_DIRECTORY.joinpath("kordevance.db")


@lru_cache(maxsize=1)
def get_engine() -> AsyncEngine:
    return create_async_engine(f"sqlite+aiosqlite:///{_DB_PATH}", pool_pre_ping=True)


async def init_db() -> None:
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.exec_driver_sql("PRAGMA journal_mode=WAL")
        await conn.run_sync(SQLModel.metadata.create_all)


def get_profile_repository() -> ProfileRepo:
    return ProfileRepository(get_engine())


ProfileRepoDep = Annotated[ProfileRepo, Depends(get_profile_repository)]
