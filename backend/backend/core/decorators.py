from functools import wraps

from backend.schemas.response import error, success


def handle_try_catch_action(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return success(result)
        except Exception as e:
            return error(str(e))

    return wrapper
