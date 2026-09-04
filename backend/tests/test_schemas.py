"""schemas 校验器与响应信封。"""

import pytest
from pydantic import ValidationError

from backend.schemas.analysis import AnalysisTrendQuery
from backend.schemas.brand import MAX_BRAND_COMPARE, TrendAllPeriodsQuery
from backend.schemas.response import error, success


class TestSplitBrandNames:
    def test_string_input_splits_and_strips(self):
        q = TrendAllPeriodsQuery(brand_names="比亚迪, 理想 ,特斯拉")
        assert q.brand_names == ["比亚迪", "理想", "特斯拉"]

    def test_list_input_joined_then_split(self):
        q = TrendAllPeriodsQuery(brand_names=["比亚迪", "理想"])
        assert q.brand_names == ["比亚迪", "理想"]

    def test_dedupes_empty_parts(self):
        q = TrendAllPeriodsQuery(brand_names=" , 比亚迪 ,, ,")
        assert q.brand_names == ["比亚迪"]

    def test_truncates_to_max_compare(self):
        names = ",".join(f"品牌{i}" for i in range(6))
        q = TrendAllPeriodsQuery(brand_names=names)
        assert len(q.brand_names) == MAX_BRAND_COMPARE
        assert q.brand_names == [f"品牌{i}" for i in range(MAX_BRAND_COMPARE)]

    def test_empty_string_rejected(self):
        with pytest.raises(ValidationError, match="不能为空"):
            TrendAllPeriodsQuery(brand_names="")

    def test_whitespace_only_rejected(self):
        with pytest.raises(ValidationError):
            TrendAllPeriodsQuery(brand_names=" , , ")

    def test_empty_list_rejected(self):
        with pytest.raises(ValidationError):
            TrendAllPeriodsQuery(brand_names=[])

    def test_data_type_default_retail(self):
        assert TrendAllPeriodsQuery(brand_names="比亚迪").data_type == "retail"

    def test_invalid_data_type_rejected(self):
        with pytest.raises(ValidationError):
            TrendAllPeriodsQuery(brand_names="比亚迪", data_type="unknown")


class TestAnalysisTrendQuery:
    def test_defaults(self):
        q = AnalysisTrendQuery()
        assert q.years == 3
        assert q.granularity == "monthly"

    @pytest.mark.parametrize("years", [1, 5, 10])
    def test_valid_years(self, years):
        assert AnalysisTrendQuery(years=years).years == years

    @pytest.mark.parametrize("years", [0, -1, 11, 100])
    def test_out_of_range_years_rejected(self, years):
        with pytest.raises(ValidationError):
            AnalysisTrendQuery(years=years)

    def test_invalid_granularity_rejected(self):
        with pytest.raises(ValidationError):
            AnalysisTrendQuery(granularity="quarterly")


class TestResponseEnvelope:
    def test_success_defaults(self):
        resp = success()
        assert resp.code == 0
        assert resp.message == "success"
        assert resp.data is None

    def test_success_with_data(self):
        resp = success([1, 2])
        assert resp.model_dump() == {"code": 0, "message": "success", "data": [1, 2]}

    def test_error_defaults(self):
        resp = error()
        assert resp.model_dump() == {"code": -1, "message": "error", "data": None}

    def test_error_with_code(self):
        resp = error(message="不存在", code=1003)
        assert (resp.code, resp.message) == (1003, "不存在")
