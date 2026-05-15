from dataclasses import dataclass

from fastapi import status

from backend.core.error_codes import (
    DATABASE_ERROR,
    EXTERNAL_SOURCE_ERROR,
    INTERNAL_ERROR,
    PERMISSION_DENIED,
    RESOURCE_NOT_FOUND,
    VALIDATION_ERROR,
)


@dataclass
class AppError(Exception):
    message: str
    code: int = INTERNAL_ERROR
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR


class ValidationAppError(AppError):
    def __init__(self, message: str = "参数校验失败"):
        super().__init__(
            message=message,
            code=VALIDATION_ERROR,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class PermissionAppError(AppError):
    def __init__(self, message: str = "权限不足"):
        super().__init__(
            message=message,
            code=PERMISSION_DENIED,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class NotFoundAppError(AppError):
    def __init__(self, message: str = "资源不存在"):
        super().__init__(
            message=message,
            code=RESOURCE_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ExternalSourceAppError(AppError):
    def __init__(self, message: str = "外部数据源请求失败"):
        super().__init__(
            message=message,
            code=EXTERNAL_SOURCE_ERROR,
            status_code=status.HTTP_502_BAD_GATEWAY,
        )


class DatabaseAppError(AppError):
    def __init__(self, message: str = "数据库操作失败"):
        super().__init__(
            message=message,
            code=DATABASE_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
