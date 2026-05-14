from typing import Any

from pydantic import BaseModel


class ApiResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Any = None


def success(data: Any = None) -> ApiResponse:
    return ApiResponse(code=0, message="success", data=data)


def error(message: str = "error", code: int = -1) -> ApiResponse:
    return ApiResponse(code=code, message=message, data=None)