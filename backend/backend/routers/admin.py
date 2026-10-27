import hmac

from fastapi import APIRouter, Depends, Header, Request, status
from fastapi.responses import StreamingResponse

from backend import config
from backend.core.csrf import verify_csrf
from backend.core.deps import DbSession
from backend.core.error_codes import PERMISSION_DENIED
from backend.core.exceptions import AppError
from backend.core.rate_limit import client_ip, import_password_lock
from backend.services.refresh_orchestrator import refresh_all_stream

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["admin"],
    dependencies=[Depends(verify_csrf)],
)


def _require_admin_password(provided: str, client: str) -> None:
    expected = config.ADMIN_REFRESH_PASSWORD
    if not expected:
        raise AppError(
            message="未配置刷新密码",
            code=PERMISSION_DENIED,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    import_password_lock.check(client)
    if not provided or not hmac.compare_digest(provided, expected):
        import_password_lock.fail(client)
        raise AppError(
            message="密码错误",
            code=PERMISSION_DENIED,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    import_password_lock.success(client)


@router.post("/data/refresh/stream")
def trigger_refresh_stream(
    db: DbSession,
    request: Request,
    x_admin_password: str = Header(default="", alias="X-Admin-Password"),
):
    _require_admin_password(x_admin_password, client_ip(request))
    return StreamingResponse(
        refresh_all_stream(db),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
