import logging

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from backend.core.error_codes import (
    DATABASE_ERROR,
    EXTERNAL_SOURCE_ERROR,
    INTERNAL_ERROR,
    PERMISSION_DENIED,
    RESOURCE_NOT_FOUND,
    VALIDATION_ERROR,
)
from backend.core.exceptions import AppError, DatabaseAppError, ExternalSourceAppError
from backend.schemas.response import error

logger = logging.getLogger(__name__)


def _http_error_code(status_code: int) -> int:
    if status_code in {401, 403}:
        return PERMISSION_DENIED
    if status_code == 404:
        return RESOURCE_NOT_FOUND
    if status_code == 422:
        return VALIDATION_ERROR
    return INTERNAL_ERROR


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content=error(message=exc.message, code=exc.code).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_error_handler(_: Request, exc: RequestValidationError):
        logger.warning("request validation failed: %s", exc.errors())
        return JSONResponse(
            status_code=422,
            content=error(message="参数校验失败", code=VALIDATION_ERROR).model_dump(),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException):
        code = _http_error_code(exc.status_code)
        detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content=error(message=detail, code=code).model_dump(),
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(_: Request, exc: SQLAlchemyError):
        logger.exception("database operation failed")
        app_error = DatabaseAppError()
        return JSONResponse(
            status_code=app_error.status_code,
            content=error(message=app_error.message, code=DATABASE_ERROR).model_dump(),
        )

    @app.exception_handler(httpx.HTTPError)
    async def external_source_exception_handler(_: Request, exc: httpx.HTTPError):
        logger.exception("external source request failed")
        app_error = ExternalSourceAppError()
        return JSONResponse(
            status_code=app_error.status_code,
            content=error(message=app_error.message, code=EXTERNAL_SOURCE_ERROR).model_dump(),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception):
        logger.exception("unhandled exception")
        app_error = AppError(
            message="服务内部错误",
            code=INTERNAL_ERROR,
            status_code=500,
        )
        return JSONResponse(
            status_code=app_error.status_code,
            content=error(message=app_error.message, code=app_error.code).model_dump(),
        )
