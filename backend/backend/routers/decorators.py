import inspect
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any

from backend.schemas.response import success


def handle_success_response[R, **P](
    func: Callable[P, R | Awaitable[R]],
) -> Callable[P, Awaitable[Any]]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
        result = func(*args, **kwargs)
        if inspect.isawaitable(result):
            result = await result
        return success(result)

    return wrapper
