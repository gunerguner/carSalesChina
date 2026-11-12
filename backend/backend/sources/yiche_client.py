"""易车销量采集。overall salesType: 1=零售,3=产量,4=出口；brand saleType: 1=零售,3=出口,4=产量（3/4 与总体相反）。"""

import json
import logging
import time
from collections import defaultdict
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from itertools import batched

from backend.types import BrandSalesRecord, OverallSalesRecord
from backend.sources.fetch_result import (
    KeyedSliceResult,
    SliceResult,
    SourceFetchResult,
)
from backend.sources.yiche_common import (
    BRAND_FETCH_DIMS,
    OVERALL_FETCH_DIMS,
    BrandFetchDim,
    OverallFetchDim,
    _BRAND_API_URL,
    _BRAND_BATCH_SIZE,
    _BRAND_WORKERS,
    _CID,
    _OVERALL_API_URL,
    _api_error,
    _brand_headers,
    _md5_sign,
    _safe_get_json,
)

logger = logging.getLogger(__name__)

# 测试与外部兼容：继续从本模块导入纯函数/维度常量
__all__ = [
    "BRAND_FETCH_DIMS",
    "OVERALL_FETCH_DIMS",
    "BrandFetchDim",
    "OverallFetchDim",
    "YicheBrandClient",
    "YicheOverallClient",
    "_api_error",
    "_md5_sign",
    "_safe_get_json",
]


class YicheOverallClient:
    """易车总体销量客户端（carserialsalestrend 接口）。"""

    def _fetch_overall(self, dim: OverallFetchDim) -> SliceResult[list[dict]]:
        tag = f"saleType={dim.sale_type},timeType=0,levelType={dim.level_type}"
        resp = _safe_get_json(
            _OVERALL_API_URL,
            params={
                "app_ver": "",
                "levelType": dim.level_type,
                "timeType": 0,
                "salesType": dim.sale_type,
            },
            timeout=30,
            tag=tag,
        )
        if not resp.ok:
            return SliceResult(data=[], error=resp.error)
        if err := _api_error(resp.body or {}, tag, expect_int=True):
            logger.warning("易车总体 API 返回异常 (%s): %s", tag, err.split(": ", 1)[-1])
            return SliceResult(data=[], error=err)
        return SliceResult(data=resp.body.get("data") or [])

    @staticmethod
    def _normalize_overall_row(raw: dict, dim: OverallFetchDim) -> OverallSalesRecord | None:
        sales_num = raw.get("salesNum")
        if sales_num is None:
            return None
        # 出口口径 API 返回原始台数（辆），零售/产量已是万辆；统一换算为万辆入库
        sales = float(sales_num)
        if dim.data_type == "export":
            sales = sales / 10000
        return {
            "year": raw.get("year"),
            "month": raw.get("month", 0),
            "sales": sales,
            "data_type": dim.data_type,
            "date_type": "monthly",
            "level_type": dim.level_label,
        }

    @staticmethod
    def _collect_overall_rows(
        raw_rows: list[dict], dim: OverallFetchDim
    ) -> list[OverallSalesRecord]:
        return [
            row
            for raw in raw_rows
            if (row := YicheOverallClient._normalize_overall_row(raw, dim)) is not None
        ]

    def fetch_overall_sales(self) -> SourceFetchResult:
        """拉取总体销量；任一维度接口失败则 ok=False（仍合并已成功维度的数据）。"""
        records: list[OverallSalesRecord] = []
        errors: list[str] = []
        for dim in OVERALL_FETCH_DIMS:
            result = self._fetch_overall(dim)
            if not result.ok and result.error:
                errors.append(result.error)
            records.extend(self._collect_overall_rows(result.data, dim))
            logger.info(
                "总体销量已拉取: saleType=%s, timeType=0, levelType=%s, 记录数=%s",
                dim.sale_type, dim.level_type, len(result.data),
            )
            time.sleep(0.5)
        return SourceFetchResult(records=records, ok=len(errors) == 0, errors=errors)


class YicheBrandClient:
    """易车品牌销量客户端（get_master_sales_history 接口）。"""

    def _fetch_brand_batch(
        self,
        master_ids: list[int],
        dim: BrandFetchDim,
        last_sale_time: str,
    ) -> SliceResult[dict[int, list[dict]]]:
        tag = dim.log_tag(master_ids)
        param = dim.to_api_param(master_ids, last_sale_time)
        param_json = json.dumps(param, separators=(",", ":"), ensure_ascii=False)
        ts = int(time.time() * 1000)
        resp = _safe_get_json(
            _BRAND_API_URL,
            params={"cid": _CID, "param": param_json},
            headers=_brand_headers(param_json, ts, param["cityId"]),
            timeout=15,
            tag=tag,
        )
        if not resp.ok:
            return SliceResult(data={}, error=resp.error)
        if err := _api_error(resp.body or {}, tag, expect_int=False):
            logger.warning("品牌销量 API 异常 (%s): %s", tag, err.split(": ", 1)[-1])
            return SliceResult(data={}, error=err)
        series_list: list[list[dict]] = resp.body.get("data") or []
        return SliceResult(data=dict(zip(master_ids, series_list)))

    @staticmethod
    def _normalize_brand_row(
        row: dict,
        master_id: int,
        data_type: str,
        level_label: str,
    ) -> BrandSalesRecord | None:
        year = row.get("year")
        month = row.get("month")
        num = row.get("num")
        if year is None or month is None or num is None:
            return None
        return {
            "year": year,
            "month": month,
            "master_id": master_id,
            "sales_volume": float(num),
            "data_type": data_type,
            "date_type": "monthly",
            "level_type": level_label,
        }

    @staticmethod
    def _collect_brand_rows(
        brand_map: dict[int, list[dict]],
        dim: BrandFetchDim,
    ) -> list[BrandSalesRecord]:
        return [
            normalized
            for master_id, series in brand_map.items()
            for row in series
            if (
                normalized := YicheBrandClient._normalize_brand_row(
                    row=row,
                    master_id=master_id,
                    data_type=dim.data_type,
                    level_label=dim.level_label,
                )
            )
            is not None
        ]

    def fetch_brand_sales(
        self,
        master_ids: list[int],
        on_progress: Callable[[int, int], None] | None = None,
    ) -> SourceFetchResult:
        """并发拉取所有品牌的各维度销量数据；任一批次接口失败则 ok=False。"""
        if not master_ids:
            return SourceFetchResult()

        last_sale_time = date.today().isoformat()
        batches = list(batched(master_ids, _BRAND_BATCH_SIZE))
        aggregated: dict[str, dict[int, list[dict]]] = defaultdict(dict)
        errors: list[str] = []
        total_tasks = len(BRAND_FETCH_DIMS) * len(batches)
        completed_tasks = 0

        def _run(
            dim: BrandFetchDim, batch: tuple[int, ...]
        ) -> KeyedSliceResult[dict[int, list[dict]]]:
            result = self._fetch_brand_batch(list(batch), dim, last_sale_time)
            return KeyedSliceResult(key=dim.dim_key(), data=result.data, error=result.error)

        with ThreadPoolExecutor(max_workers=_BRAND_WORKERS) as executor:
            futures = {
                executor.submit(_run, dim, batch): (dim, batch)
                for dim in BRAND_FETCH_DIMS
                for batch in batches
            }
            for future in as_completed(futures):
                out = future.result()
                if not out.ok and out.error:
                    errors.append(out.error)
                aggregated[out.key].update(out.data)
                completed_tasks += 1
                if on_progress:
                    on_progress(completed_tasks, total_tasks)

        records: list[BrandSalesRecord] = []
        for dim in BRAND_FETCH_DIMS:
            records.extend(self._collect_brand_rows(aggregated.get(dim.dim_key(), {}), dim))

        ok = len(errors) == 0
        logger.info(
            "品牌销量拉取完成: 品牌数=%s, 维度数=%s, 总记录数=%s, ok=%s",
            len(master_ids), len(BRAND_FETCH_DIMS), len(records), ok,
        )
        return SourceFetchResult(records=records, ok=ok, errors=errors)
