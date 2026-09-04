"""market_service / brand_service：SQLite 内存库查询。"""

import pytest

from backend.core.exceptions import NotFoundAppError
from backend.services.brand_service import get_all_brand_meta, get_brand_trend_all_periods
from backend.services.market_service import get_raw_market_data
from tests.conftest import add_brand_meta, add_brand_sales, add_sales


@pytest.fixture
def seeded_brands(db_session):
    byd = add_brand_meta(db_session, brand_name="比亚迪", brand_name_en="byd", master_id=100)
    li = add_brand_meta(db_session, brand_name="理想", brand_name_en="lixiang", master_id=101)
    add_brand_meta(db_session, brand_name="大众", brand_name_en="volkswagen", master_id=102)
    add_brand_meta(db_session, brand_name="", brand_name_en="noname", master_id=None)
    db_session.commit()

    add_brand_sales(db_session, brand_id=byd.id, year=2024, month=1, sales_volume=20.0)
    add_brand_sales(db_session, brand_id=byd.id, year=2024, month=2, sales_volume=22.5)
    add_brand_sales(db_session, brand_id=li.id, year=2024, month=1, sales_volume=3.0)
    # 应被过滤：非零售 / 非 all 级别 / 非月度
    add_brand_sales(db_session, brand_id=byd.id, year=2024, month=1, sales_volume=99.0, data_type="production")
    add_brand_sales(db_session, brand_id=byd.id, year=2024, month=1, sales_volume=88.0, level_type="nev")
    add_brand_sales(db_session, brand_id=byd.id, year=2024, month=1, sales_volume=77.0, date_type="quarterly")
    db_session.commit()
    return {"byd": byd, "li": li}


class TestGetRawMarketData:
    def test_returns_all_monthly_rows_ordered(self, db_session):
        add_sales(db_session, year=2024, month=2, sales=200.0)
        add_sales(db_session, year=2023, month=12, sales=150.0)
        add_sales(db_session, year=2024, month=1, sales=100.0, level_type="nev")
        db_session.commit()

        rows = get_raw_market_data(db_session)
        assert [(r["year"], r["month"], r["level_type"]) for r in rows] == [
            (2023, 12, "all"),
            (2024, 1, "nev"),
            (2024, 2, "all"),
        ]
        assert rows[0]["data_type"] == "retail"
        assert rows[0]["sales"] == 150.0

    def test_includes_all_data_types(self, db_session):
        add_sales(db_session, year=2024, month=1, sales=10.0, data_type="production")
        add_sales(db_session, year=2024, month=1, sales=5.0, data_type="export")
        db_session.commit()
        rows = get_raw_market_data(db_session)
        assert {r["data_type"] for r in rows} == {"production", "export"}

    def test_excludes_non_monthly(self, db_session):
        add_sales(db_session, year=2024, month=1, sales=10.0, date_type="quarterly")
        db_session.commit()
        assert get_raw_market_data(db_session) == []

    def test_none_sales_becomes_zero(self, db_session):
        add_sales(db_session, year=2024, month=1, sales=None)
        db_session.commit()
        assert get_raw_market_data(db_session)[0]["sales"] == 0

    def test_empty_db(self, db_session):
        assert get_raw_market_data(db_session) == []


class TestGetAllBrandMeta:
    def test_returns_all_rows_and_filters_empty_names(self, db_session, seeded_brands):
        rows = get_all_brand_meta(db_session)
        # 排序在 MySQL/SQLite 的 collation 下可能不同，只断言集合与结构
        assert {r["brand_name"] for r in rows} == {"大众", "比亚迪", "理想"}
        assert all(set(r) == {"brand_id", "brand_name"} for r in rows)
        assert all(r["brand_id"] for r in rows)

    def test_empty_db(self, db_session):
        assert get_all_brand_meta(db_session) == []


class TestGetBrandTrendAllPeriods:
    def test_returns_series_per_brand_in_request_order(self, db_session, seeded_brands):
        series = get_brand_trend_all_periods(db_session, ["理想", "比亚迪"], "retail")
        assert [s["brand_name"] for s in series] == ["理想", "比亚迪"]
        byd = series[1]
        assert byd["monthly_data"] == [
            {"year": 2024, "month": 1, "sales": 20.0},
            {"year": 2024, "month": 2, "sales": 22.5},
        ]

    def test_filters_by_data_type(self, db_session, seeded_brands):
        series = get_brand_trend_all_periods(db_session, ["比亚迪"], "production")
        assert series[0]["monthly_data"] == [
            {"year": 2024, "month": 1, "sales": 99.0}
        ]

    def test_filters_level_and_date_type(self, db_session, seeded_brands):
        """retail 查询只取 level=all 的月度数据（99/88/77 为干扰行）。"""
        series = get_brand_trend_all_periods(db_session, ["比亚迪"], "retail")
        assert [p["sales"] for p in series[0]["monthly_data"]] == [20.0, 22.5]

    def test_missing_brand_raises_not_found(self, db_session, seeded_brands):
        with pytest.raises(NotFoundAppError, match="蔚来"):
            get_brand_trend_all_periods(db_session, ["比亚迪", "蔚来"], "retail")

    def test_brand_with_no_sales_returns_empty_series(self, db_session, seeded_brands):
        series = get_brand_trend_all_periods(db_session, ["大众"], "retail")
        assert series == [{"brand_name": "大众", "monthly_data": []}]

    def test_none_sales_volume_becomes_zero(self, db_session, seeded_brands):
        add_brand_sales(
            db_session, brand_id=seeded_brands["byd"].id, year=2024, month=3, sales_volume=None
        )
        db_session.commit()
        series = get_brand_trend_all_periods(db_session, ["比亚迪"], "retail")
        assert series[0]["monthly_data"][-1]["sales"] == 0
