"""进程内限流：密码连续失败锁定。"""

import pytest

from backend.core.exceptions import AppError


def test_import_password_lockout():
    from backend.core.rate_limit import FailureLockout

    lock = FailureLockout(max_failures=5, lock_seconds=900)
    for _ in range(5):
        lock.fail("10.0.0.1")
    with pytest.raises(AppError) as caught:
        lock.check("10.0.0.1")
    assert caught.value.status_code == 429


def test_import_password_success_clears_failures():
    from backend.core.rate_limit import FailureLockout

    lock = FailureLockout(max_failures=5, lock_seconds=900)
    for _ in range(4):
        lock.fail("10.0.0.2")
    lock.success("10.0.0.2")
    lock.check("10.0.0.2")
    for _ in range(4):
        lock.fail("10.0.0.2")
    lock.check("10.0.0.2")
