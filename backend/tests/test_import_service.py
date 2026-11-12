"""import_service：刷新入库编排。

- 纯函数（状态聚合、记录归一化）直接测；
- refresh_brand_meta 用 SQLite + 仓库内真实 meta_data.yaml；
- refresh_sales_data / refresh_origin_data mock 外部客户端与 _batch_upsert（后者是
  MySQL 方言 SQL，SQLite 无法执行，方言正确性由编译断言守护）。
"""

from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml
from sqlmodel import select

from backend.core.exceptions import AppError, ExternalSourceAppError
from backend.models.brand import BrandMeta
from backend.models.overall import SalesData
from backend.services import import_service
from backend.services.import_service import (
    BRAND_SALES_FIELDS,
    OVERALL_SALES_FIELDS,
    _batch_upsert,
    _normalize_brand_records,
    _refresh_status,
    refresh_brand_meta,
    refresh_origin_data,
    refresh_sales_data,
)
from backend.sources.fetch_result import SourceFetchResult
from tests.conftest import add_brand_meta


def _fr(records=None, ok=True, errors=None):
    return SourceFetchResult(records=records or [], ok=ok, errors=errors or [])


class TestRefreshStatus:
    @pytest.mark.parametrize(
        ("overall_ok", "brand_ok", "expected"),
        [
            (True, True, "success"),
            (False, False, "failed"),
            (True, False, "partial_failure"),
            (False, True, "partial_failure"),
        ],
    )
    def test_combinations(self, overall_ok, brand_ok, expected):
        assert _refresh_status(overall_ok, brand_ok) == expected


class TestNormalizeBrandRecords:
    @pytest.fixture
    def mapping(self):
        return {100: 1, 101: 2}

    def test_maps_master_id_to_brand_id(self, mapping):
        records = [
            {
                "year": 2024,
                "month": 1,
                "master_id": 100,
                "sales_volume": 10.0,
                "data_type": "retail",
                "date_type": "monthly",
                "level_type": "all",
            }
        ]
        rows = _normalize_brand_records(records, mapping)
        assert rows == [
            {
                "year": 2024,
                "month": 1,
                "brand_id": 1,
                "sales_volume": 10.0,
                "data_type": "retail",
                "date_type": "monthly",
                "level_type": "all",
            }
        ]

    def test_drops_unknown_master_id(self, mapping):
        records = [{"year": 2024, "month": 1, "master_id": 999, "sales_volume": 1.0}]
        assert _normalize_brand_records(records, mapping) == []

    def test_defaults_for_missing_optional_fields(self, mapping):
        rows = _normalize_brand_records(
            [{"year": 2024, "month": 2, "master_id": 101, "sales_volume": None}], mapping
        )
        assert rows[0]["sales_volume"] is None
        assert rows[0]["data_type"] == "retail"
        assert rows[0]["date_type"] == "monthly"
        assert rows[0]["level_type"] == "all"


class TestBatchUpsert:
    def _capture(self, db_session, monkeypatch):
        captured = []

        def fake_execute(statement, parameters=None):
            captured.append((statement, parameters))

        monkeypatch.setattr(db_session, "execute", fake_execute)
        monkeypatch.setattr(db_session, "commit", lambda: None)
        return captured

    def test_empty_records_short_circuits(self, db_session, monkeypatch):
        captured = self._capture(db_session, monkeypatch)
        assert _batch_upsert(db_session, SalesData, [], OVERALL_SALES_FIELDS) == 0
        assert captured == []

    def test_generates_mysql_on_duplicate_key_sql(self, db_session, monkeypatch):
        """守护 MySQL 方言 SQL：ON DUPLICATE KEY UPDATE 与字段列表。"""
        from sqlalchemy.dialects import mysql

        captured = self._capture(db_session, monkeypatch)
        records = [
            {
                "year": 2024,
                "month": 1,
                "sales": 1.0,
                "data_type": "retail",
                "date_type": "monthly",
                "level_type": "all",
            }
        ]
        count = _batch_upsert(db_session, SalesData, records, OVERALL_SALES_FIELDS)
        assert count == 1
        stmt, params = captured[0]
        sql = str(stmt.compile(dialect=mysql.dialect()))
        assert "INSERT INTO sales_data" in sql
        assert "ON DUPLICATE KEY UPDATE" in sql
        for field in OVERALL_SALES_FIELDS:
            assert f"{field}=VALUES({field})" in sql
        assert params == [
            {
                "year": 2024,
                "month": 1,
                "sales": 1.0,
                "data_type": "retail",
                "date_type": "monthly",
                "level_type": "all",
            }
        ]

    def test_params_only_keep_declared_fields(self, db_session, monkeypatch):
        captured = self._capture(db_session, monkeypatch)
        records = [{"year": 2024, "month": 1, "sales": 2.0, "extra": "ignored"}]
        _batch_upsert(db_session, SalesData, records, OVERALL_SALES_FIELDS)
        assert set(captured[0][1][0]) == set(OVERALL_SALES_FIELDS)

    def test_batches_by_500(self, db_session, monkeypatch):
        captured = self._capture(db_session, monkeypatch)
        records = [
            {"year": 2024, "month": 1, "sales": float(i)} for i in range(1001)
        ]
        # 补齐 fields 缺省键
        for rec in records:
            rec.update(
                {"data_type": "retail", "date_type": "monthly", "level_type": "all"}
            )
        count = _batch_upsert(db_session, SalesData, records, OVERALL_SALES_FIELDS)
        assert count == 1001
        batch_sizes = [len(params) for _, params in captured]
        assert sum(batch_sizes) == 1001
        assert len(batch_sizes) > 1
        assert all(size <= 500 for size in batch_sizes)


class TestRefreshBrandMeta:
    def test_first_run_inserts_all_brands_from_yaml(self, db_session):
        result = refresh_brand_meta(db_session)
        total_brands = len(yaml.safe_load(Path(import_service.META_DATA_PATH).read_text("utf-8"))["brands"])
        assert result == {"inserted": total_brands, "updated": 0, "total": total_brands, "status": "success"}
        assert len(db_session.exec(select(BrandMeta)).all()) == total_brands

    def test_second_run_is_idempotent(self, db_session):
        refresh_brand_meta(db_session)
        result = refresh_brand_meta(db_session)
        assert result["inserted"] == 0
        assert result["updated"] == 0
        assert result["status"] == "success"

    def test_detects_master_id_drift_and_updates(self, db_session):
        refresh_brand_meta(db_session)
        row = db_session.exec(
            BrandMeta.__table__.select().where(BrandMeta.brand_name == "奔驰")
        ).first()
        row_id, original = row.id, row.master_id
        db_session.execute(
            BrandMeta.__table__.update().where(BrandMeta.id == row_id).values(master_id=999)
        )
        db_session.commit()

        result = refresh_brand_meta(db_session)
        assert result["updated"] == 1
        refreshed = db_session.get(BrandMeta, row_id)
        assert refreshed.master_id == original

    def test_detects_en_name_drift_and_updates(self, db_session):
        refresh_brand_meta(db_session)
        row = db_session.exec(
            BrandMeta.__table__.select().where(BrandMeta.brand_name == "奔驰")
        ).first()
        row_id, original = row.id, row.brand_name_en
        db_session.execute(
            BrandMeta.__table__.update()
            .where(BrandMeta.id == row_id)
            .values(brand_name_en="wrong-en")
        )
        db_session.commit()

        result = refresh_brand_meta(db_session)
        assert result["updated"] == 1
        refreshed = db_session.get(BrandMeta, row_id)
        assert refreshed.brand_name_en == original

    def _write_yaml(self, tmp_path, payload):
        path = tmp_path / "meta_test.yaml"
        path.write_text(yaml.safe_dump(payload), encoding="utf-8")
        return path

    def test_skips_when_no_brands(self, db_session, monkeypatch, tmp_path):
        path = self._write_yaml(tmp_path, {"brands": {}})
        monkeypatch.setattr(import_service, "META_DATA_PATH", path)
        assert refresh_brand_meta(db_session) == {
            "status": "skipped",
            "reason": "no brands in yaml",
        }

    def test_rejects_non_dict_root(self, db_session, monkeypatch, tmp_path):
        path = self._write_yaml(tmp_path, ["not", "a", "dict"])
        monkeypatch.setattr(import_service, "META_DATA_PATH", path)
        with pytest.raises(AppError) as exc_info:
            refresh_brand_meta(db_session)
        assert "格式错误" in exc_info.value.message

    def test_missing_file_raises(self, db_session, monkeypatch, tmp_path):
        monkeypatch.setattr(
            import_service, "META_DATA_PATH", tmp_path / "not_exist.yaml"
        )
        with pytest.raises(AppError) as exc_info:
            refresh_brand_meta(db_session)
        assert "不存在" in exc_info.value.message

    def test_skips_entries_without_name(self, db_session, monkeypatch, tmp_path):
        path = self._write_yaml(
            tmp_path,
            {"brands": {"ok": {"name": "有名字", "master_id": 1}, "bad": {"master_id": 2}}},
        )
        monkeypatch.setattr(import_service, "META_DATA_PATH", path)
        result = refresh_brand_meta(db_session)
        assert result["inserted"] == 1
        assert result["total"] == 2
