"""yiche：签名、错误判定与维度编码纯函数。"""

import pytest

from backend.sources.yiche_client import (
    BRAND_FETCH_DIMS,
    OVERALL_FETCH_DIMS,
    BrandFetchDim,
    _api_error,
    _md5_sign,
)

class TestMd5Sign:
    def test_known_digest(self):
        # 固定输入的签名快照：防止拼接格式被无意改动
        assert _md5_sign('{"k":1}', 1717000000) == "38ae928455fc01ed5de44c2e127ac533"

    def test_changes_with_ts(self):
        assert _md5_sign('{"k":1}', 1717000000) != _md5_sign('{"k":1}', 1717000001)

    def test_changes_with_param(self):
        assert _md5_sign('{"k":1}', 1) != _md5_sign('{"k":2}', 1)


class TestApiError:
    def test_int_status_one_ok_when_expect_int(self):
        assert _api_error({"status": 1}, "tag", expect_int=True) is None

    def test_str_status_one_rejected_when_expect_int(self):
        assert _api_error({"status": "1"}, "tag", expect_int=True) == "tag: status!=1"

    def test_str_status_one_ok_when_not_expect_int(self):
        assert _api_error({"status": "1"}, "tag", expect_int=False) is None

    def test_int_status_one_ok_when_not_expect_int(self):
        assert _api_error({"status": 1}, "tag", expect_int=False) is None

    @pytest.mark.parametrize("expect_int", [True, False])
    def test_status_zero_returns_tagged_error(self, expect_int):
        err = _api_error({"status": 0, "message": "失败"}, "tag", expect_int=expect_int)
        assert err == "tag: 失败"

    def test_missing_message_falls_back(self):
        assert _api_error({"status": 0}, "tag", expect_int=True) == "tag: status!=1"


class TestOverallDims:
    def test_dims_cover_3_data_types_x_3_levels(self):
        assert len(OVERALL_FETCH_DIMS) == 9  # 3 data_type × 3 level

    def test_includes_retail_all_dim(self):
        retail_all = next(
            d for d in OVERALL_FETCH_DIMS
            if d.data_type == "retail" and d.level_label == "all"
        )
        assert retail_all.sale_type == 1
        assert retail_all.level_type == -1

    def test_export_coded_as_sale_type_4(self):
        export_dims = [d for d in OVERALL_FETCH_DIMS if d.data_type == "export"]
        assert len(export_dims) == 3
        assert all(d.sale_type == 4 for d in export_dims)

    def test_level_coding(self):
        by_label = {d.level_label: d.level_type for d in OVERALL_FETCH_DIMS if d.data_type == "retail"}
        assert by_label == {"all": -1, "nev": 4, "bev": 5}


class TestBrandDims:
    def test_dims_cover_retail_levels_plus_production_export(self):
        assert len(BRAND_FETCH_DIMS) == 5  # retail×3 + production + export

    def test_sale_type_coding_opposite_to_overall(self):
        """品牌接口 3=出口、4=产量，与总体（3=产量、4=出口）相反。"""
        by_type = {d.data_type: d.sale_type for d in BRAND_FETCH_DIMS}
        assert by_type == {"retail": 1, "production": 4, "export": 3}

    def test_only_retail_has_level_breakdown(self):
        labels_by_type: dict[str, list[str]] = {}
        for d in BRAND_FETCH_DIMS:
            labels_by_type.setdefault(d.data_type, []).append(d.level_label)
        assert labels_by_type == {
            "retail": ["all", "nev", "bev"],
            "production": ["all"],
            "export": ["all"],
        }

    def test_dim_key_omits_energy_for_all(self):
        assert BrandFetchDim(1, -1, "retail", "all").dim_key() == "sale=1"
        assert BrandFetchDim(1, 1, "retail", "nev").dim_key() == "sale=1|energy=1"
        assert BrandFetchDim(3, -1, "export", "all").dim_key() == "sale=3"
        assert BrandFetchDim(4, 3, "retail", "bev").dim_key() == "sale=4|energy=3"

    def test_log_tag_contains_key_and_batch(self):
        tag = BrandFetchDim(1, -1, "retail", "all").log_tag([5, 6])
        assert tag == "sale=1 batch=[5, 6]"

    def test_to_api_param(self):
        param = BrandFetchDim(1, 1, "retail", "nev").to_api_param([5, 6], "2024-06-01")
        assert param == {
            "masterIds": "5,6",
            "cityId": 0,
            "isNewEnergy": 1,
            "manu": -1,
            "saleType": 1,
            "lastSaleTime": "2024-06-01",
        }


