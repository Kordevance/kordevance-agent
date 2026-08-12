from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from importlib.metadata import version

from fastapi import FastAPI

from kordevance.application.config.exception_handlers import register_exception_handlers
from kordevance.application.config.logs import setup_logging
from kordevance.application.config.middleware import register_middlewares
from kordevance.application.dependencies.sql_store_adapter import init_db
from kordevance.application.routers.profile import router as profile_router

setup_logging()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await init_db()
    yield


app = FastAPI(
    title="kordevance API",
    description="REST API for the kordevance platform",
    version=version("kordevance"),
    root_path="/api",
    lifespan=lifespan,
)


register_middlewares(app)
register_exception_handlers(app)

app.include_router(profile_router)
