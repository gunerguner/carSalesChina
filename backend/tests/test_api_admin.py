"""API 层：CSRF 保护与 /api/v1/admin/data/refresh/stream（SSE）。"""

import json

from starlette.requests import Request

from backend.core.csrf import CSRF_COOKIE_NAME, CSRF_HEADER_NAME, verify_csrf


def _get_token(client) -> str:
    """任意 GET 请求触发中间件下发 csrf_token Cookie。"""
    client.get("/api/v1/market/raw")
    return client.cookies.get(CSRF_COOKIE_NAME)


class TestVerifyCsrf:
    def test_safe_method_skips_check(self):
        request = Request(
            {
                "type": "http",
                "http_version": "1.1",
                "method": "GET",
                "scheme": "http",
                "path": "/",
                "raw_path": b"/",
                "query_string": b"",
                "headers": [],
                "client": ("testclient", 50000),
                "server": ("testserver", 80),
            }
        )
        assert verify_csrf(request) is None


class TestCsrfCookieMiddleware:
    def test_first_get_sets_cookie(self, client):
        resp = client.get("/api/v1/market/raw")
        assert CSRF_COOKIE_NAME in resp.cookies
        token = resp.cookies[CSRF_COOKIE_NAME]
        assert len(token) == 64  # token_hex(32)

    def test_get_is_not_blocked(self, client):
        assert client.get("/api/v1/market/raw").status_code == 200


class TestAdminRefreshStreamCsrf:
    URL = "/api/v1/admin/data/refresh/stream"

    def test_post_without_csrf_rejected(self, client):
        resp = client.post(self.URL)
        assert resp.status_code == 403
        assert resp.json()["code"] == 1002

    def test_post_with_cookie_but_no_header_rejected(self, client):
        _get_token(client)
        resp = client.post(self.URL)
        assert resp.status_code == 403

    def test_post_with_header_but_no_cookie_rejected(self, client):
        resp = client.post(self.URL, headers={CSRF_HEADER_NAME: "whatever"})
        assert resp.status_code == 403

    def test_post_with_mismatched_token_rejected(self, client):
        _get_token(client)
        resp = client.post(self.URL, headers={CSRF_HEADER_NAME: "not-the-token"})
        assert resp.status_code == 403

    def test_post_with_matching_token_streams_sse(self, client, monkeypatch):
        from backend.routers import admin as admin_router
        from backend.services.progress import format_sse

        frames = [
            format_sse("progress", {"phase": "brand_meta", "status": "running"}),
            format_sse("done", {"status": "success"}),
        ]
        monkeypatch.setattr(
            admin_router, "refresh_all_stream", lambda db: iter(frames)
        )

        token = _get_token(client)
        resp = client.post(self.URL, headers={CSRF_HEADER_NAME: token})
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/event-stream")
        assert resp.headers["cache-control"] == "no-cache"

        events = [
            line.removeprefix("event: ")
            for line in resp.text.splitlines()
            if line.startswith("event: ")
        ]
        assert events == ["progress", "done"]
        # 最后一帧是 done 事件
        done_data = json.loads(
            [
                line.removeprefix("data: ")
                for line in resp.text.splitlines()
                if line.startswith("data: ")
            ][-1]
        )
        assert done_data["status"] == "success"
