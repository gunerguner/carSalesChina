"""import_service：销量/国别刷新编排（mock 外部客户端与 _batch_upsert）。"""

from types import SimpleNamespace

import pytest

from backend.core.exceptions import ExternalSourceAppError
from backend.services import import_service
from backend.services.import_service import (
    BRAND_SALES_FIELDS,
    OVERALL_SALES_FIELDS,
    refresh_origin_data,
    refresh_sales_data,
)
from backend.sources.fetch_result import SourceFetchResult
from tests.conftest import add_brand_meta


def _fr(records=None, ok=True, errors=None):
    return SourceFetchResult(records=records or [], ok=ok, errors=errors or [])


class TestRefreshSalesData:
    @pytest.fixture
    def brands(self, db_session):
        add_brand_meta(db_session, brand_name="比亚迪", brand_name_en="byd", master_id=100)
        add_brand_meta(db_session, brand_name="理想", brand_name_en="lixiang", master_id=101)
        add_brand_meta(db_session, brand_name="无ID品牌", brand_name_en="noid", master_id=None)
        db_session.commit()

    @pytest.fixture
    def upsert_spy(self, monkeypatch):
        calls = []

        def fake_upsert(db, model, records, fields):
            calls.append((model.__tablename__, len(records), fields))
            return len(records)

        monkeypatch.setattr(import_service, "_batch_upsert", fake_upsert)
        return calls

    def _patch_clients(self, monkeypatch, overall_fr, brand_fr=None, captured=None):
        monkeypatch.setattr(
            import_service.yiche_overall_client,
            "fetch_overall_sales",
            lambda: overall_fr,
        )
        if brand_fr is not None:
            def fake_brand(master_ids, on_progress=None):
                if captured is not None:
                    captured.append((master_ids, on_progress))
                return brand_fr

            monkeypatch.setattr(
                import_service.yiche_brand_client, "fetch_brand_sales", fake_brand
            )

    def test_all_sources_ok_returns_success_counts(self, db_session, brands, upsert_spy, monkeypatch):
        overall = _fr([{"year": 2024, "month": 1, "sales": 1.0}])
        brand = _fr(
            [
                {"year": 2024, "month": 1, "master_id": 100, "sales_volume": 10.0},
                {"year": 2024, "month": 1, "master_id": 999, "sales_volume": 99.0},  # 未知品牌被过滤
            ]
        )
        self._patch_clients(monkeypatch, overall, brand)

        result = refresh_sales_data(db_session)
        assert result["status"] == "success"
        assert result["overall_count"] == 1
        assert result["brand_count"] == 1
        assert result["records_count"] == 2
        assert result["source_errors"] == {"overall": None, "brand": None}
        # upsert 调用顺序：先总体后品牌，且只查有 master_id 的品牌
        assert [c[0] for c in upsert_spy] == ["sales_data", "brand_sales"]
        assert upsert_spy[0][2] == OVERALL_SALES_FIELDS
        assert upsert_spy[1][2] == BRAND_SALES_FIELDS

    def test_partial_failure_when_brand_fails(self, db_session, brands, upsert_spy, monkeypatch):
        self._patch_clients(
            monkeypatch,
            _fr([{"year": 2024, "month": 1, "sales": 1.0}]),
            _fr(ok=False, errors=["brand: boom"]),
        )
        result = refresh_sales_data(db_session)
        assert result["status"] == "partial_failure"
        assert result["source_errors"]["brand"] == "brand: boom"

    def test_all_failed_raises_external_source_error(self, db_session, brands, upsert_spy, monkeypatch):
        self._patch_clients(
            monkeypatch,
            _fr(ok=False, errors=["overall: down"]),
            _fr(ok=False, errors=["brand: down"]),
        )
        with pytest.raises(ExternalSourceAppError):
            refresh_sales_data(db_session)

    def test_no_brands_with_master_id_skips_brand_fetch(self, db_session, upsert_spy, monkeypatch):
        add_brand_meta(db_session, brand_name="无ID", brand_name_en="noid", master_id=None)
        db_session.commit()
        self._patch_clients(monkeypatch, _fr([{"year": 2024, "month": 1, "sales": 1.0}]))
        result = refresh_sales_data(db_session)
        assert result["status"] == "success"
        assert result["brand_count"] == 0
        assert [c[0] for c in upsert_spy] == ["sales_data"]

    def test_passes_master_ids_and_progress_callback(self, db_session, brands, upsert_spy, monkeypatch):
        captured = []
        self._patch_clients(
            monkeypatch,
            _fr([{"year": 2024, "month": 1, "sales": 1.0}]),
            _fr([{"year": 2024, "month": 1, "master_id": 100, "sales_volume": 10.0}]),
            captured=captured,
        )
        seen = []
        refresh_sales_data(db_session, on_brand_progress=lambda cur, total: seen.append((cur, total)))
        master_ids, on_progress = captured[0]
        assert sorted(master_ids) == [100, 101]
        on_progress(1, 2)
        assert seen == [(1, 2)]

    def test_reporter_receives_progress(self, db_session, brands, upsert_spy, monkeypatch):
        self._patch_clients(
            monkeypatch,
            _fr([{"year": 2024, "month": 1, "sales": 1.0}]),
            _fr([{"year": 2024, "month": 1, "master_id": 100, "sales_volume": 10.0}]),
        )
        calls = []
        reporter = SimpleNamespace(
            phase_progress=lambda phase, cur, total, detail=None: calls.append(
                (phase, cur, total, detail)
            )
        )
        refresh_sales_data(db_session, reporter=reporter)
        assert calls[0][0] == "sales"
        assert "总体销量" in calls[0][3]


class TestRefreshOriginData:
    @pytest.fixture
    def upsert_spy(self, monkeypatch):
        calls = []

        def fake_upsert(db, model, records, fields):
            calls.append((model.__tablename__, len(records)))
            return len(records)

        monkeypatch.setattr(import_service, "_batch_upsert", fake_upsert)
        return calls

    def test_origin_ok_returns_success_counts(self, db_session, upsert_spy, monkeypatch):
        rows = [{"year": 2024, "month": 1, "origin": "自主", "sales_volume": 60.0}]
        monkeypatch.setattr(
            import_service.cpca_client,
            "get_country_data",
            lambda: _fr(rows),
        )
        result = refresh_origin_data(db_session)
        assert result == {
            "origin_count": 1,
            "records_count": 1,
            "status": "success",
            "source_errors": {"origin": None},
        }
        assert upsert_spy == [("origin_share_data", 1)]

    def test_failed_raises_external_source_error(self, db_session, upsert_spy, monkeypatch):
        monkeypatch.setattr(
            import_service.cpca_client,
            "get_country_data",
            lambda: _fr(ok=False, errors=["akshare down"]),
        )
        with pytest.raises(ExternalSourceAppError):
            refresh_origin_data(db_session)
