"""analysis_service：SQLite 内存库 + 种子数据。

重点守护的业务规则：
- NEV 渗透率 = nev / all（仅 retail + monthly 参与）；
- 纯电占新能源比 bev/nev，插混 phev = max(nev - bev, 0)；
- 国别字段经 origin_field_map 映射，占比基于同期总量；
- years 决定起始年份（以当前年为锚）。
"""

import pytest

from backend.core.exceptions import AppError, ValidationAppError
from backend.services import analysis_service
from backend.services.analysis_periods import PeriodKey
from backend.services.analysis_service import (
    _percent,
    _start_year,
    get_nev_breakdown,
    get_nev_share_trend,
    get_origin_share_trend,
)


class TestPureHelpers:
    def test_percent(self):
        assert _percent(30, 100) == 30.0
        assert _percent(1, 3) == 33.33  # 保留两位小数
        assert _percent(10, 0) == 0  # 除零保护

    def test_start_year_anchored_to_current_year(self):
        from datetime import datetime

        assert _start_year(3) == datetime.now().year - 2
        assert _start_year(1) == datetime.now().year

    @pytest.mark.parametrize("years", [0, -1])
    def test_start_year_rejects_non_positive(self, years):
        with pytest.raises(ValidationAppError):
            _start_year(years)

    def test_nev_share_row(self):
        row = analysis_service._nev_share_row(
            PeriodKey(2024, 3), {"all": 200.0, "nev": 50.0}
        )
        assert row == {
            "year": 2024,
            "month": 3,
            "nev_penetration_rate": 25.0,
            "total_sales": 200.0,
            "nev_sales": 50.0,
        }

    def test_nev_share_row_missing_levels_default_zero(self):
        row = analysis_service._nev_share_row(PeriodKey(2024), {})
        assert row["nev_penetration_rate"] == 0
        assert row["total_sales"] == 0

    def test_nev_breakdown_row_phev_is_nev_minus_bev(self):
        row = analysis_service._nev_breakdown_row(
            PeriodKey(2024, 3), {"nev": 80.0, "bev": 20.0}
        )
        assert row["phev_sales"] == 60.0
        assert row["bev_ratio"] == 25.0
        assert row["phev_ratio"] == 75.0
        assert row["hybrid_sales"] == 0
        assert row["hybrid_ratio"] == 0

    def test_nev_breakdown_row_clamps_negative_phev(self):
        """bev > nev（脏数据）时插混钳制为 0 而非负数。"""
        row = analysis_service._nev_breakdown_row(
            PeriodKey(2024, 3), {"nev": 10.0, "bev": 30.0}
        )
        assert row["phev_sales"] == 0
        assert row["phev_ratio"] == 0

    def test_origin_share_row_maps_cn_to_en(self):
        row = analysis_service._origin_share_row(
            PeriodKey(2024, 1), {"自主": 60.0, "未知国别": 40.0}, total=100.0
        )
        assert row["domestic"] == 60.0
        assert "未知国别" not in row  # 未映射国别只计入分母，不产出字段
        for field in ("german", "japanese", "american", "european", "french", "korean"):
            assert row[field] == 0


class TestNevShareTrend:
    def test_monthly(self, db_session, analysis_dataset):
        rows = get_nev_share_trend(db_session, years=2, granularity="monthly")
        assert [(r["year"], r["month"]) for r in rows] == [
            (analysis_dataset["current_year"] - 1, 1),
            (analysis_dataset["current_year"] - 1, 2),
            (analysis_dataset["current_year"], 1),
        ]
        assert [r["nev_penetration_rate"] for r in rows] == [30.0, 40.0, 40.0]
        assert rows[0]["total_sales"] == 100.0
        assert rows[0]["nev_sales"] == 30.0

    def test_yearly_aggregates_months(self, db_session, analysis_dataset):
        cy = analysis_dataset["current_year"]
        rows = get_nev_share_trend(db_session, years=2, granularity="yearly")
        assert [(r["year"], "month" in r) for r in rows] == [(cy - 1, False), (cy, False)]
        assert rows[0]["total_sales"] == 300.0  # 100 + 200
        assert rows[0]["nev_sales"] == 110.0  # 30 + 80
        assert rows[0]["nev_penetration_rate"] == 36.67

    def test_years_filters_old_data(self, db_session, analysis_dataset):
        rows = get_nev_share_trend(db_session, years=1, granularity="monthly")
        assert len(rows) == 1
        assert rows[0]["year"] == analysis_dataset["current_year"]

    def test_excludes_non_retail_and_non_monthly(self, db_session, analysis_dataset):
        """production 与 quarterly 行不应混入（数据集里埋了 999/888）。"""
        rows = get_nev_share_trend(db_session, years=2, granularity="monthly")
        assert all(r["total_sales"] < 900 for r in rows)

    def test_empty_db_returns_empty_list(self, db_session):
        assert get_nev_share_trend(db_session, years=3, granularity="monthly") == []


class TestNevBreakdown:
    def test_monthly(self, db_session, analysis_dataset):
        rows = get_nev_breakdown(db_session, years=2, granularity="monthly")
        first = rows[0]
        assert (first["nev_sales"], first["bev_sales"], first["phev_sales"]) == (30.0, 10.0, 20.0)
        assert (first["bev_ratio"], first["phev_ratio"]) == (33.33, 66.67)

    def test_yearly(self, db_session, analysis_dataset):
        rows = get_nev_breakdown(db_session, years=2, granularity="yearly")
        first = rows[0]
        assert (first["nev_sales"], first["bev_sales"]) == (110.0, 30.0)
        assert first["phev_sales"] == 80.0
        assert first["bev_ratio"] == 27.27

    def test_empty_db_returns_empty_list(self, db_session):
        assert get_nev_breakdown(db_session, years=3, granularity="yearly") == []


class TestOriginShareTrend:
    def test_monthly(self, db_session, origin_dataset):
        rows = get_origin_share_trend(db_session, years=2, granularity="monthly")
        assert len(rows) == 2
        first, second = rows
        assert (first["year"], first["month"]) == (
            origin_dataset["current_year"] - 1,
            1,
        )
        assert (first["domestic"], first["german"], first["japanese"]) == (60.0, 25.0, 15.0)
        assert (second["domestic"], second["german"]) == (70.0, 30.0)
        assert second["japanese"] == 0  # 缺失国别补 0

    def test_unmapped_origin_counts_toward_total_only(self, db_session, origin_dataset):
        from tests.conftest import add_origin_share

        cy = origin_dataset["current_year"]
        # (CY-1, 1) 追加未映射国别 100 → 总量 100→200，自主占比 60→30
        add_origin_share(db_session, year=cy - 1, month=1, origin="其他", sales_volume=100.0)
        db_session.commit()
        rows = get_origin_share_trend(db_session, years=2, granularity="monthly")
        assert rows[0]["domestic"] == 30.0

    def test_yearly(self, db_session, origin_dataset):
        rows = get_origin_share_trend(db_session, years=2, granularity="yearly")
        assert len(rows) == 1
        assert rows[0]["domestic"] == 65.0  # (60+70) / (60+25+15+70+30) = 130/200

    def test_empty_map_raises_app_error(self, db_session, origin_dataset, monkeypatch):
        monkeypatch.setattr(analysis_service, "ORIGIN_FIELD_MAP", {})
        with pytest.raises(AppError) as exc_info:
            get_origin_share_trend(db_session, years=2, granularity="monthly")
        assert "origin_field_map" in exc_info.value.message

    def test_empty_db_returns_empty_list(self, db_session):
        assert get_origin_share_trend(db_session, years=3, granularity="monthly") == []
