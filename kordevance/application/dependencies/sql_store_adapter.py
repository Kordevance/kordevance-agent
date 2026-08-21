from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import SQLModel

from kordevance.adapters.crypto.fernet_encryptor import FernetEncryptor
from kordevance.adapters.sql_store.device_registration_repository import DeviceRegistrationRepository
from kordevance.adapters.sql_store.event_repository import EventRepository
from kordevance.adapters.sql_store.goal_repository import GoalRepository
from kordevance.adapters.sql_store.llm_provider_repository import LLMProviderRepository
from kordevance.adapters.sql_store.model_assignment_repository import ModelAssignmentRepository
from kordevance.adapters.sql_store.profile_repository import ProfileRepository
from kordevance.adapters.sql_store.task_repository import TaskRepository
from kordevance.application import _WORKING_DIRECTORY
from kordevance.application.config.secrets import load_or_create_encryption_key
from kordevance.domain.ports.device_registration_repository import DeviceRegistrationRepo
from kordevance.domain.ports.encryptor import Encryptor
from kordevance.domain.ports.event_repository import EventRepo
from kordevance.domain.ports.goal_repository import GoalRepo
from kordevance.domain.ports.llm_provider_repository import LLMProviderRepo
from kordevance.domain.ports.model_assignment_repository import ModelAssignmentRepo
from kordevance.domain.ports.profile_repository import ProfileRepo
from kordevance.domain.ports.task_repository import TaskRepo

_DB_PATH = _WORKING_DIRECTORY.joinpath("kordevance.db")


@lru_cache(maxsize=1)
def get_engine() -> AsyncEngine:
    return create_async_engine(f"sqlite+aiosqlite:///{_DB_PATH}", pool_pre_ping=True)


async def init_db() -> None:
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.exec_driver_sql("PRAGMA journal_mode=WAL")
        await conn.run_sync(SQLModel.metadata.create_all)


@lru_cache(maxsize=1)
def get_encryptor() -> Encryptor:
    return FernetEncryptor(load_or_create_encryption_key())


def get_profile_repository() -> ProfileRepo:
    return ProfileRepository(get_engine())


def get_llm_provider_repository() -> LLMProviderRepo:
    return LLMProviderRepository(get_engine(), get_encryptor())


def get_model_assignment_repository() -> ModelAssignmentRepo:
    return ModelAssignmentRepository(get_engine())


def get_goal_repository() -> GoalRepo:
    return GoalRepository(get_engine())


def get_task_repository() -> TaskRepo:
    return TaskRepository(get_engine())


def get_event_repository() -> EventRepo:
    return EventRepository(get_engine())


def get_device_registration_repository() -> DeviceRegistrationRepo:
    return DeviceRegistrationRepository(get_engine())


ProfileRepoDep = Annotated[ProfileRepo, Depends(get_profile_repository)]
ModelProviderDep = Annotated[LLMProviderRepo, Depends(get_llm_provider_repository)]
ModelAssignmentDep = Annotated[ModelAssignmentRepo, Depends(get_model_assignment_repository)]
GoalRepoDep = Annotated[GoalRepo, Depends(get_goal_repository)]
TaskRepoDep = Annotated[TaskRepo, Depends(get_task_repository)]
EventRepoDep = Annotated[EventRepo, Depends(get_event_repository)]
