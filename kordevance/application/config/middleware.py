import logging
import time
from typing import Any

from fastapi import FastAPI, Request


def register_middlewares(app: FastAPI) -> None:
    @app.middleware("http")
    async def log_requests(request: Request, call_next: Any) -> Any:
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        logging.info(f"{request.method} {request.url} - {response.status_code} ({duration:.2f}s)")
        return response
