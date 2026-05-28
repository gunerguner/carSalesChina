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


def _error_response(status_code: int, message: str, code: int) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=error(message=message, code=code).model_dump(),
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError):
        return _error_response(exc.status_code, exc.message, exc.code)

    @app.exception_handler(RequestValidationError)
    async def request_validation_error_handler(_: Request, exc: RequestValidationError):
        logger.warning("request validation failed: %s", exc.errors())
        return _error_response(422, "参数校验失败", VALIDATION_ERROR)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException):
        code = _http_error_code(exc.status_code)
        detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        return _error_response(exc.status_code, detail, code)

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(_: Request, exc: SQLAlchemyError):
        logger.exception("database operation failed")
        app_error = DatabaseAppError()
        return _error_response(app_error.status_code, app_error.message, DATABASE_ERROR)

    @app.exception_handler(httpx.HTTPError)
    async def external_source_exception_handler(_: Request, exc: httpx.HTTPError):
        logger.exception("external source request failed")
        app_error = ExternalSourceAppError()
        return _error_response(
            app_error.status_code, app_error.message, EXTERNAL_SOURCE_ERROR
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception):
        logger.exception("unhandled exception")
        app_error = AppError(
            message="服务内部错误",
            code=INTERNAL_ERROR,
            status_code=500,
        )
        return _error_response(app_error.status_code, app_error.message, app_error.code)
