import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from kordevance.application.schemas.error_response import ErrorResponse
from kordevance.exceptions import (
    BadRequestError,
    ItemNotFoundError
)

logger = logging.getLogger(__name__)


def _log_context(request: Request) -> str:
    client = request.client.host if request.client else "unknown"
    return f"{request.method} {request.url.path} from {client}"


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(BadRequestError)
    async def bad_request_exception_handler(request: Request, exc: BadRequestError) -> JSONResponse:
        logger.warning("Bad request on %s: %s", _log_context(request), exc, exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(error="Bad Request", reason=str(exc)).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        reason = ", ".join(f"{' -> '.join(str(loc) for loc in e['loc'])}: {e['msg']}" for e in exc.errors())
        logger.warning("Validation error on %s: %s", _log_context(request), exc.errors(), exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(error="Bad Request", reason=reason).model_dump(),
        )

    @app.exception_handler(ItemNotFoundError)
    async def item_not_found_exception_handler(request: Request, exc: ItemNotFoundError) -> JSONResponse:
        logger.info("Item not found on %s: %s", _log_context(request), exc)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(error="Not Found", reason=str(exc)).model_dump(),
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error("Unhandled exception on %s: %s", _log_context(request), exc, exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="Internal Server Error",
                reason="An unexpected error occurred. Please try again later.",
            ).model_dump(),
        )
