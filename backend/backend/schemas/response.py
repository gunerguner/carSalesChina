from pydantic import BaseModel
from typing import Any


class ApiResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Any = None


def success(data: Any = None) -> dict:
    return {"code": 0, "message": "success", "data": data}


def error(message: str = "error", code: int = -1) -> dict:
    return {"code": code, "message": message, "data": None}