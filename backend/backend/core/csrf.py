import hmac
import secrets

from fastapi import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

CSRF_COOKIE_NAME = "csrf_token"
CSRF_HEADER_NAME = "x-csrf-token"
CSRF_SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


class CSRFCookieMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        if CSRF_COOKIE_NAME not in request.cookies:
            response.set_cookie(
                key=CSRF_COOKIE_NAME,
                value=secrets.token_hex(32),
                path="/",
                samesite="lax",
                httponly=False,
            )
        return response


def verify_csrf(request: Request):
    if request.method in CSRF_SAFE_METHODS:
        return

    cookie_token = request.cookies.get(CSRF_COOKIE_NAME, "")
    header_token = request.headers.get(CSRF_HEADER_NAME, "")

    if not cookie_token or not header_token:
        raise HTTPException(status_code=403, detail="CSRF token missing")

    if not hmac.compare_digest(cookie_token, header_token):
        raise HTTPException(status_code=403, detail="CSRF token mismatch")
