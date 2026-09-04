"""全局异常处理器：HTTPException 状态码映射、SQLAlchemy、httpx。"""

import httpx
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from backend.core.error_codes import (
    DATABASE_ERROR,
    EXTERNAL_SOURCE_ERROR,
    INTERNAL_ERROR,
    PERMISSION_DENIED,
    RESOURCE_NOT_FOUND,
    VALIDATION_ERROR,
)
from backend.core.exceptions import DatabaseAppError, ExternalSourceAppError


def _boom(client, monkeypatch, exc: BaseException):
    from backend.routers import market

    def raise_exc(db):
        raise exc

    monkeypatch.setattr(market, "get_raw_market_data", raise_exc)
    return client.get("/api/v1/market/raw")


class TestHttpExceptionMapping:
    def test_401_maps_to_permission_denied(self, client, monkeypatch):
        resp = _boom(client, monkeypatch, HTTPException(status_code=401, detail="未登录"))
        assert resp.status_code == 401
        assert resp.json()["code"] == PERMISSION_DENIED
        assert resp.json()["message"] == "未登录"

    def test_404_maps_to_not_found(self, client, monkeypatch):
        resp = _boom(client, monkeypatch, HTTPException(status_code=404, detail="gone"))
        assert resp.status_code == 404
        assert resp.json()["code"] == RESOURCE_NOT_FOUND

    def test_422_maps_to_validation(self, client, monkeypatch):
        resp = _boom(client, monkeypatch, HTTPException(status_code=422, detail="bad"))
        assert resp.status_code == 422
        assert resp.json()["code"] == VALIDATION_ERROR

    def test_other_status_maps_to_internal(self, client, monkeypatch):
        resp = _boom(client, monkeypatch, HTTPException(status_code=418, detail="teapot"))
        assert resp.status_code == 418
        assert resp.json()["code"] == INTERNAL_ERROR

    def test_non_str_detail_is_stringified(self, client, monkeypatch):
        resp = _boom(
            client, monkeypatch, HTTPException(status_code=400, detail={"field": "x"})
        )
        assert resp.status_code == 400
        assert "field" in resp.json()["message"]


class TestInfrastructureExceptions:
    def test_sqlalchemy_error_envelope(self, client, monkeypatch):
        resp = _boom(client, monkeypatch, SQLAlchemyError("db down"))
        assert resp.status_code == 500
        body = resp.json()
        assert body["code"] == DATABASE_ERROR
        assert body["message"] == DatabaseAppError().message

    def test_httpx_error_envelope(self, client, monkeypatch):
        resp = _boom(client, monkeypatch, httpx.HTTPError("timeout"))
        assert resp.status_code == 502
        body = resp.json()
        assert body["code"] == EXTERNAL_SOURCE_ERROR
        assert body["message"] == ExternalSourceAppError().message
