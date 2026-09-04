"""yiche_client：签名、错误判定、维度编码、行归一化与拉取编排。

重点守护的业务规则：
- 出口口径销量 ÷10000 换算为万辆（零售/产量不换算）；
- 总体与品牌的 saleType 编码相反（overall: 1/3/4=零售/产量/出口；brand: 1/3/4=零售/出口/产量）；
- 任一维度失败 → ok=False 但仍合并成功维度数据。
"""

import pytest

from backend.sources import yiche_client
from backend.sources.fetch_result import HttpJsonResult, SliceResult
from backend.sources.yiche_client import (
    BRAND_FETCH_DIMS,
    OVERALL_FETCH_DIMS,
    BrandFetchDim,
    YicheBrandClient,
    YicheOverallClient,
    _api_error,
    _md5_sign,
    _safe_get_json,
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
        assert _api_error({"status": "1"}, "tag", expect_int=True) is not None

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
    def test_nine_dims(self):
        assert len(OVERALL_FETCH_DIMS) == 9  # 3 data_type × 3 level

    def test_first_dim_is_retail_all(self):
        assert OVERALL_FETCH_DIMS[0].sale_type == 1
        assert OVERALL_FETCH_DIMS[0].level_type == -1
        assert OVERALL_FETCH_DIMS[0].data_type == "retail"
        assert OVERALL_FETCH_DIMS[0].level_label == "all"

    def test_export_coded_as_sale_type_4(self):
        export_dims = [d for d in OVERALL_FETCH_DIMS if d.data_type == "export"]
        assert len(export_dims) == 3
        assert all(d.sale_type == 4 for d in export_dims)

    def test_level_coding(self):
        by_label = {d.level_label: d.level_type for d in OVERALL_FETCH_DIMS if d.data_type == "retail"}
        assert by_label == {"all": -1, "nev": 4, "bev": 5}


class TestBrandDims:
    def test_five_dims(self):
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


class TestNormalizeOverallRow:
    def test_retail_not_scaled(self):
        dim = OVERALL_FETCH_DIMS[0]  # retail/all
        row = YicheOverallClient._normalize_overall_row(
            {"year": 2024, "month": 3, "salesNum": 12.5}, dim
        )
        assert row == {
            "year": 2024,
            "month": 3,
            "sales": 12.5,
            "data_type": "retail",
            "date_type": "monthly",
            "level_type": "all",
        }

    def test_export_divided_by_10000(self):
        dim = next(d for d in OVERALL_FETCH_DIMS if d.data_type == "export")
        row = YicheOverallClient._normalize_overall_row(
            {"year": 2024, "month": 3, "salesNum": 500000}, dim
        )
        assert row["sales"] == 50.0

    def test_missing_sales_num_returns_none(self):
        assert YicheOverallClient._normalize_overall_row({"year": 2024}, OVERALL_FETCH_DIMS[0]) is None

    def test_month_defaults_zero(self):
        row = YicheOverallClient._normalize_overall_row(
            {"year": 2024, "salesNum": 1.0}, OVERALL_FETCH_DIMS[0]
        )
        assert row["month"] == 0

    def test_collect_filters_none(self):
        dim = OVERALL_FETCH_DIMS[0]
        rows = YicheOverallClient._collect_overall_rows(
            [
                {"year": 2024, "month": 1, "salesNum": 1.0},
                {"year": 2024, "month": 2},  # 无 salesNum → 跳过
                {"year": 2024, "month": 3, "salesNum": 3.0},
            ],
            dim,
        )
        assert [r["month"] for r in rows] == [1, 3]


class TestFetchOverallSales:
    @pytest.fixture(autouse=True)
    def no_sleep(self, monkeypatch):
        monkeypatch.setattr(yiche_client.time, "sleep", lambda _: None)

    @staticmethod
    def _install(client, results_by_data_type):
        def fake_fetch(dim):
            if dim.data_type in results_by_data_type:
                return results_by_data_type[dim.data_type]
            return SliceResult(data=[])

        client._fetch_overall = fake_fetch

    def test_all_ok_merges_records_from_all_dims(self):
        client = YicheOverallClient()
        self._install(
            client,
            {
                "retail": SliceResult(
                    data=[{"year": 2024, "month": 1, "salesNum": 10.0}]
                ),
                "export": SliceResult(
                    data=[{"year": 2024, "month": 1, "salesNum": 20000.0}]
                ),
            },
        )
        result = client.fetch_overall_sales()
        assert result.ok
        assert result.errors == []
        retail = [r for r in result.records if r["data_type"] == "retail"]
        export = [r for r in result.records if r["data_type"] == "export"]
        assert len(retail) == 3  # retail 有 3 个 level 维度，各 1 条
        assert len(export) == 3
        assert all(r["sales"] == 2.0 for r in export)  # 20000 → 2 万辆

    def test_one_dim_failed_still_returns_others(self):
        client = YicheOverallClient()
        self._install(
            client,
            {
                "retail": SliceResult(data=[], error="retail: 网络超时"),
                "export": SliceResult(
                    data=[{"year": 2024, "month": 1, "salesNum": 10000.0}]
                ),
            },
        )
        result = client.fetch_overall_sales()
        assert not result.ok
        assert result.errors == ["retail: 网络超时"] * 3  # retail 的 all/nev/bev 三个维度各报一次
        assert len(result.records) == 3  # export 三个 level 维度的数据仍在


class TestNormalizeBrandRow:
    def test_full_row(self):
        row = YicheBrandClient._normalize_brand_row(
            {"year": 2024, "month": 5, "num": "31.5"}, master_id=100,
            data_type="retail", level_label="all",
        )
        assert row == {
            "year": 2024,
            "month": 5,
            "master_id": 100,
            "sales_volume": 31.5,
            "data_type": "retail",
            "date_type": "monthly",
            "level_type": "all",
        }

    @pytest.mark.parametrize("missing", ["year", "month", "num"])
    def test_missing_required_field_returns_none(self, missing):
        raw = {"year": 2024, "month": 5, "num": 1.0}
        raw.pop(missing)
        assert (
            YicheBrandClient._normalize_brand_row(
                raw, master_id=1, data_type="retail", level_label="all"
            )
            is None
        )

    def test_collect_aggregates_by_master(self):
        dim = BRAND_FETCH_DIMS[0]
        records = YicheBrandClient._collect_brand_rows(
            {
                100: [{"year": 2024, "month": 1, "num": 1.0}, {"year": 2024, "month": 2, "num": 2.0}],
                101: [{"year": 2024, "month": 1, "num": 3.0}],
            },
            dim,
        )
        assert len(records) == 3
        assert {r["master_id"] for r in records} == {100, 101}


class TestFetchBrandSales:
    @staticmethod
    def _install(client, fail_data_types=()):
        def fake_fetch(master_ids, dim, last_sale_time):
            if dim.data_type in fail_data_types:
                return SliceResult(data={}, error=f"{dim.dim_key()}: boom")
            return SliceResult(
                data={mid: [{"year": 2024, "month": 1, "num": float(mid)}] for mid in master_ids}
            )

        client._fetch_brand_batch = fake_fetch

    def test_empty_master_ids_returns_empty_ok(self):
        result = YicheBrandClient().fetch_brand_sales([])
        assert result.records == []
        assert result.ok

    def test_concurrent_batches_and_progress(self):
        client = YicheBrandClient()
        self._install(client)
        master_ids = list(range(1, 8))  # 7 品牌 → 2 批（5+2）
        seen = []
        result = client.fetch_brand_sales(master_ids, on_progress=lambda cur, total: seen.append((cur, total)))

        total_tasks = len(BRAND_FETCH_DIMS) * 2  # 5 维度 × 2 批
        assert seen[-1] == (total_tasks, total_tasks)
        assert [cur for cur, _ in seen] == list(range(1, total_tasks + 1))
        assert result.ok
        # 每个维度 × 每个 master_id 一条记录
        assert len(result.records) == len(BRAND_FETCH_DIMS) * len(master_ids)
        assert {r["master_id"] for r in result.records} == set(master_ids)

    def test_one_dim_failed_marks_not_ok(self):
        client = YicheBrandClient()
        self._install(client, fail_data_types=("export",))
        result = client.fetch_brand_sales([1, 2])
        assert not result.ok
        assert any("boom" in e for e in result.errors)
        # 其他维度的记录仍然保留
        assert any(r["data_type"] == "retail" for r in result.records)


class TestSafeGetJson:
    def test_success(self, monkeypatch):
        class FakeResp:
            def raise_for_status(self):
                return None

            def json(self):
                return {"status": 1, "data": []}

        monkeypatch.setattr(yiche_client.httpx, "get", lambda *a, **k: FakeResp())
        result = _safe_get_json("http://example.test", timeout=1, tag="t")
        assert result.ok
        assert result.body == {"status": 1, "data": []}

    def test_exception_returns_error(self, monkeypatch):
        def boom(*a, **k):
            raise yiche_client.httpx.ConnectError("timeout")

        monkeypatch.setattr(yiche_client.httpx, "get", boom)
        result = _safe_get_json("http://example.test", timeout=1, tag="overall")
        assert not result.ok
        assert result.error is not None
        assert result.error.startswith("overall:")


class TestFetchOverallHttp:
    def test_http_error(self, monkeypatch):
        monkeypatch.setattr(
            yiche_client,
            "_safe_get_json",
            lambda *a, **k: HttpJsonResult(error="tag: timeout"),
        )
        result = YicheOverallClient()._fetch_overall(OVERALL_FETCH_DIMS[0])
        assert not result.ok
        assert result.data == []
        assert result.error == "tag: timeout"

    def test_api_status_error(self, monkeypatch):
        monkeypatch.setattr(
            yiche_client,
            "_safe_get_json",
            lambda *a, **k: HttpJsonResult(body={"status": 0, "message": "限流"}),
        )
        result = YicheOverallClient()._fetch_overall(OVERALL_FETCH_DIMS[0])
        assert not result.ok
        assert result.data == []
        assert result.error is not None
        assert "限流" in result.error

    def test_ok_empty_data(self, monkeypatch):
        monkeypatch.setattr(
            yiche_client,
            "_safe_get_json",
            lambda *a, **k: HttpJsonResult(body={"status": 1}),
        )
        result = YicheOverallClient()._fetch_overall(OVERALL_FETCH_DIMS[0])
        assert result.ok
        assert result.data == []


class TestFetchBrandBatchHttp:
    def test_http_error(self, monkeypatch):
        monkeypatch.setattr(
            yiche_client,
            "_safe_get_json",
            lambda *a, **k: HttpJsonResult(error="tag: down"),
        )
        result = YicheBrandClient()._fetch_brand_batch(
            [1], BRAND_FETCH_DIMS[0], "2024-01-01"
        )
        assert not result.ok
        assert result.data == {}

    def test_api_status_error(self, monkeypatch):
        monkeypatch.setattr(
            yiche_client,
            "_safe_get_json",
            lambda *a, **k: HttpJsonResult(body={"status": "0", "message": "no"}),
        )
        result = YicheBrandClient()._fetch_brand_batch(
            [1], BRAND_FETCH_DIMS[0], "2024-01-01"
        )
        assert not result.ok
        assert result.data == {}

    def test_ok_zips_master_ids(self, monkeypatch):
        monkeypatch.setattr(
            yiche_client,
            "_safe_get_json",
            lambda *a, **k: HttpJsonResult(
                body={"status": "1", "data": [[{"year": 2024, "month": 1, "num": 1}]]}
            ),
        )
        result = YicheBrandClient()._fetch_brand_batch(
            [100], BRAND_FETCH_DIMS[0], "2024-01-01"
        )
        assert result.ok
        assert list(result.data.keys()) == [100]
