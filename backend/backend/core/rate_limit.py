"""进程内限流。单 worker 下按 IP 计数即可。"""

import time
from collections import defaultdict
from threading import Lock

from fastapi import Request, status

from backend.core.error_codes import PERMISSION_DENIED
from backend.core.exceptions import AppError


def client_ip(request: Request) -> str:
    """限流键：优先取反向代理转发的首个 IP。"""
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded.strip():
        return forwarded.split(",")[0].strip()
    if request.client is None:
        return "unknown"
    return request.client.host


class FailureLockout:
    """连续失败达到上限后锁定一段时间。"""

    def __init__(self, *, max_failures: int, lock_seconds: int) -> None:
        self.max_failures = max_failures
        self.lock_seconds = lock_seconds
        self._failures: dict[str, list[float]] = defaultdict(list)
        self._locked_until: dict[str, float] = {}
        self._mu = Lock()

    def check(self, key: str) -> None:
        now = time.monotonic()
        with self._mu:
            until = self._locked_until.get(key, 0.0)
        if until > now:
            raise AppError(
                message="密码错误次数过多，请稍后再试",
                code=PERMISSION_DENIED,
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            )

    def fail(self, key: str) -> None:
        now = time.monotonic()
        with self._mu:
            recent = [t for t in self._failures[key] if now - t < self.lock_seconds]
            recent.append(now)
            if len(recent) >= self.max_failures:
                self._locked_until[key] = now + self.lock_seconds
                self._failures[key] = []
            else:
                self._failures[key] = recent

    def success(self, key: str) -> None:
        with self._mu:
            self._failures.pop(key, None)
            self._locked_until.pop(key, None)


import_password_lock = FailureLockout(max_failures=5, lock_seconds=15 * 60)
