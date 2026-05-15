import inspect
import logging
from functools import wraps

import httpx
from sqlalchemy.exc import SQLAlchemyError

from backend.core.exceptions import (
    AppError,
    DatabaseAppError,
    ExternalSourceAppError,
)
from backend.schemas.response import success

logger = logging.getLogger(__name__)


def handle_try_catch_action(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            if inspect.isawaitable(result):
                result = await result
            return success(result)
        except (AppError,):
            raise
        except httpx.HTTPError as exc:
            logger.exception("admin action failed by external source")
            raise ExternalSourceAppError() from exc
        except SQLAlchemyError as exc:
            logger.exception("admin action failed by database error")
            raise DatabaseAppError() from exc
        except Exception:
            logger.exception("admin action failed with unexpected exception")
            raise

    return wrapper
