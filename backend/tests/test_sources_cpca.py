"""cpca_client：日期/数值解析、DataFrame 转换与客户端结果封装。

akshare 的真实网络调用不在单测范围（_fetch_country_records 被 mock）。
"""

import numpy as np
import pandas as pd
import pytest

from backend.sources import cpca_client
from backend.sources.cpca_client import (
    CpcaClient,
    _fetch_country_records,
    _parse_month,
    _to_float,
    _transform_country,
    _try_parse_month,
)
from backend.sources.fetch_result import SliceResult


class TestParseMonth:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("2024年1月", (2024, 1)),
            ("2024年12月", (2024, 12)),
            ("2024-01", (2024, 1)),
            ("2024-1", (2024, 1)),
            ("2024/1", (2024, 1)),
            ("2024年1月 ", (2024, 1)),  # 容忍空白
        ],
    )
    def test_valid_formats(self, raw, expected):
        assert _parse_month(raw) == expected

    @pytest.mark.parametrize("raw", ["1月", "12月", "3"])
    def test_month_only_gives_none_year(self, raw):
        year, month = _parse_month(raw)
        assert year is None
        assert month is not None

    @pytest.mark.parametrize("raw", ["abc", "2024", "2024-xx", ""])
    def test_invalid_raises(self, raw):
        with pytest.raises(ValueError):
            _parse_month(raw)

    def test_try_parse_month_swallows_error(self):
        assert _try_parse_month("abc") == (None, None)
        assert _try_parse_month("2024年3月") == (2024, 3)


class TestToFloat:
    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (np.nan, None),
            (None, None),
            ("1,234.5", 1234.5),
            ("12%", 12.0),
            ("-", None),
            ("--", None),
            ("", None),
            (" 42 ", 42.0),
            (3.14, 3.14),
            (5, 5.0),
            ("700000", 700000.0),
        ],
    )
    def test_values(self, value, expected):
        assert _to_float(value) == expected


class TestTransformCountry:
    @pytest.fixture
    def sample_df(self):
        return pd.DataFrame(
            {
                "月份": ["2024年1月", "2024年2月", "无法解析", None, "2024年3月"],
                "自主": [60.0, 70.0, 1.0, 1.0, np.nan],
                "德系": [25.0, 30.0, 2.0, 2.0, 5.0],
            }
        )

    def test_melt_to_rows(self, sample_df):
        rows = _transform_country(sample_df)
        by_key = {(r["year"], r["month"], r["origin"]): r["sales_volume"] for r in rows}
        assert by_key == {
            (2024, 1, "自主"): 60.0,
            (2024, 1, "德系"): 25.0,
            (2024, 2, "自主"): 70.0,
            (2024, 2, "德系"): 30.0,
            (2024, 3, "德系"): 5.0,  # 自主 NaN 被剔除
        }
        assert all(set(r) == {"year", "month", "origin", "sales_volume"} for r in rows)

    def test_drops_unparseable_and_missing_months(self, sample_df):
        rows = _transform_country(sample_df)
        assert all(r["year"] == 2024 for r in rows)

    def test_all_nan_values_returns_empty(self):
        df = pd.DataFrame({"月份": ["2024年1月"], "自主": [np.nan], "德系": [np.nan]})
        assert _transform_country(df) == []

    def test_empty_df(self):
        assert _transform_country(pd.DataFrame(columns=["月份", "自主"])) == []

    def test_all_invalid_months_returns_empty(self):
        df = pd.DataFrame({"月份": ["a", "b"], "自主": [1.0, 2.0]})
        assert _transform_country(df) == []


class TestCpcaClient:
    def test_ok(self, monkeypatch):
        rows = [{"year": 2024, "month": 1, "origin": "自主", "sales_volume": 60.0}]
        monkeypatch.setattr(
            cpca_client, "_fetch_country_records", lambda: SliceResult(data=rows)
        )
        result = CpcaClient().get_country_data()
        assert result.ok
        assert result.records == rows
        assert result.errors == []

    def test_error(self, monkeypatch):
        monkeypatch.setattr(
            cpca_client,
            "_fetch_country_records",
            lambda: SliceResult(data=[], error="akshare 挂了"),
        )
        result = CpcaClient().get_country_data()
        assert not result.ok
        assert result.records == []
        assert result.errors == ["akshare 挂了"]

    def test_fetch_swallows_exception(self, monkeypatch):
        def boom():
            raise RuntimeError("akshare down")

        monkeypatch.setattr(cpca_client.ak, "car_market_country_cpca", boom)
        result = _fetch_country_records()
        assert not result.ok
        assert result.data == []
        assert result.error is not None
        assert "akshare down" in result.error
