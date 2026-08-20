from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from importlib.metadata import version

from fastapi import FastAPI

from kordevance.application import _APPLICATION_NAME
from kordevance.application.config.exception_handlers import register_exception_handlers
from kordevance.application.config.logs import setup_logging
from kordevance.application.config.middleware import register_middlewares
from kordevance.application.dependencies.proxy_relay_client import get_proxy_relay_client
from kordevance.application.dependencies.secret_store_adapter import get_credential_manager
from kordevance.application.dependencies.sql_store_adapter import init_db
from kordevance.application.routers.chat import router as chat_router
from kordevance.application.routers.connectors import router as connectors_router
from kordevance.application.routers.model_assignment import router as model_assignment_router
from kordevance.application.routers.model_provider import router as provider_router
from kordevance.application.routers.profile import router as profile_router
from kordevance.domain.use_cases.device_management.handle_ensure_device_registered import (
    HandleEnsureDeviceRegistered,
)

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await init_db()

    ensure_device_registered = HandleEnsureDeviceRegistered(
        credential_manager=get_credential_manager(),
        proxy_relay_client=get_proxy_relay_client(),
    )

    await ensure_device_registered.execute()

    yield


app = FastAPI(
    title=f"{_APPLICATION_NAME} API",
    description=f"REST API for the {_APPLICATION_NAME.lower()} platform",
    version=version(_APPLICATION_NAME),
    root_path="/api",
    lifespan=lifespan,
)


register_middlewares(app)
register_exception_handlers(app)

app.include_router(profile_router)
app.include_router(provider_router)
app.include_router(model_assignment_router)
app.include_router(chat_router)
app.include_router(connectors_router)
