"""易车销量采集。overall salesType: 1=零售,3=产量；brand saleType: 1=零售,4=产量（3/4 顺序相反）。"""

import hashlib
import json
import logging
import time
import uuid
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date

import httpx

from backend.common.types import BrandSalesRecord, OverallSalesRecord
from backend.sources.fetch_result import (
    HttpJsonResult,
    KeyedSliceResult,
    SliceResult,
    SourceFetchResult,
)

logger = logging.getLogger(__name__)

_CID = "602"
_SECRET = "DB2560A6EBC65F37A0484295CD4EDD25"
_OVERALL_API_URL = (
    "https://carwebapi.yiche.com/carrankingapi/api/carserialsalestrend/search"
)
_BRAND_API_URL = (
    "https://mhapi.yiche.com/hcar/h_car/h5/api/v1/ranking/get_master_sales_history"
)
_BRAND_BATCH_SIZE = 5
_BRAND_WORKERS = 8

_OVERALL_SALE_RETAIL = 1
_OVERALL_SALE_PRODUCTION = 3
_OVERALL_LEVEL = {"all": -1, "nev": 4, "bev": 5}

_BRAND_SALE_RETAIL = 1
_BRAND_SALE_PRODUCTION = 4
_BRAND_ENERGY = {"all": -1, "nev": 1, "bev": 3}


def _md5_sign(param_json: str, ts: int) -> str:
    raw = f"cid={_CID}&param={param_json}{_SECRET}{ts}"
    return hashlib.md5(raw.encode()).hexdigest()


def _safe_get_json(
    url: str,
    *,
    params: dict | None = None,
    headers: dict | None = None,
    timeout: float,
    tag: str,
) -> HttpJsonResult:
    try:
        resp = httpx.get(url, params=params, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return HttpJsonResult(body=resp.json())
    except Exception as e:
        logger.error("易车 API 请求失败 (%s): %s", tag, e)
        return HttpJsonResult(error=f"{tag}: {e}")


def _api_error(body: dict, tag: str, *, expect_int: bool) -> str | None:
    if expect_int:
        ok = body.get("status") == 1
    else:
        ok = str(body.get("status")) == "1"
    if ok:
        return None
    msg = str(body.get("message") or "status!=1")
    return f"{tag}: {msg}"


def _brand_headers(param_json: str, ts: int, city_id: int) -> dict[str, str]:
    return {
        "x-timestamp": str(ts),
        "x-sign": _md5_sign(param_json, ts),
        "x-platform": "phone",
        "x-longitude": "",
        "x-latitude": "",
        "x-user-guid": str(uuid.uuid4()),
        "x-ip-address": "",
        "x-city-id": str(city_id),
        "User-Agent": (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
        ),
        "Referer": "https://h5mp.yiche.com/",
    }


@dataclass(frozen=True)
class OverallFetchDim:
    sale_type: int
    level_type: int
    data_type: str
    level_label: str


def _overall_dims(sale_type: int, data_type: str) -> list[OverallFetchDim]:
    return [
        OverallFetchDim(sale_type, _OVERALL_LEVEL[label], data_type, label)
        for label in ("all", "nev", "bev")
    ]


OVERALL_FETCH_DIMS = (
    _overall_dims(_OVERALL_SALE_RETAIL, "retail")
    + _overall_dims(_OVERALL_SALE_PRODUCTION, "production")
)


@dataclass(frozen=True)
class BrandFetchDim:
    sale_type: int
    energy_type: int
    data_type: str
    level_label: str

    def dim_key(self) -> str:
        parts = [f"sale={self.sale_type}"]
        if self.energy_type != _BRAND_ENERGY["all"]:
            parts.append(f"energy={self.energy_type}")
        return "|".join(parts)

    def log_tag(self, master_ids: list[int]) -> str:
        return f"{self.dim_key()} batch={master_ids!r}"

    def to_api_param(self, master_ids: list[int], last_sale_time: str) -> dict:
        return {
            "masterIds": ",".join(str(i) for i in master_ids),
            "cityId": 0,
            "isNewEnergy": self.energy_type,
            "manu": -1,
            "saleType": self.sale_type,
            "lastSaleTime": last_sale_time,
        }


def _brand_dims(sale_type: int, data_type: str) -> list[BrandFetchDim]:
    return [
        BrandFetchDim(sale_type, _BRAND_ENERGY[label], data_type, label)
        for label in ("all", "nev", "bev")
    ]


BRAND_FETCH_DIMS = [
    *_brand_dims(_BRAND_SALE_RETAIL, "retail"),
    BrandFetchDim(_BRAND_SALE_PRODUCTION, _BRAND_ENERGY["all"], "production", "all"),
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
        err = _api_error(resp.body or {}, tag, expect_int=True)
        if err:
            logger.warning("易车总体 API 返回异常 (%s): %s", tag, err.split(": ", 1)[-1])
            return SliceResult(data=[], error=err)
        return SliceResult(data=resp.body.get("data") or [])

    @staticmethod
    def _normalize_overall_row(raw: dict, dim: OverallFetchDim) -> OverallSalesRecord | None:
        sales_num = raw.get("salesNum")
        if sales_num is None:
            return None
        return {
            "year": raw.get("year"),
            "month": raw.get("month", 0),
            "sales": float(sales_num),
            "data_type": dim.data_type,
            "date_type": "monthly",
            "level_type": dim.level_label,
        }

    @staticmethod
    def _collect_overall_rows(
        raw_rows: list[dict], dim: OverallFetchDim
    ) -> list[OverallSalesRecord]:
        records: list[OverallSalesRecord] = []
        for raw in raw_rows:
            row = YicheOverallClient._normalize_overall_row(raw, dim)
            if row is not None:
                records.append(row)
        return records

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
        err = _api_error(resp.body or {}, tag, expect_int=False)
        if err:
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
        records: list[BrandSalesRecord] = []
        for master_id, series in brand_map.items():
            for row in series:
                normalized = YicheBrandClient._normalize_brand_row(
                    row=row,
                    master_id=master_id,
                    data_type=dim.data_type,
                    level_label=dim.level_label,
                )
                if normalized is not None:
                    records.append(normalized)
        return records

    def fetch_brand_sales(
        self,
        master_ids: list[int],
        last_sale_time: str = "",
    ) -> SourceFetchResult:
        """并发拉取所有品牌的各维度销量数据；任一批次接口失败则 ok=False。"""
        if not master_ids:
            return SourceFetchResult()

        if not last_sale_time:
            last_sale_time = date.today().isoformat()

        batches = [
            master_ids[i: i + _BRAND_BATCH_SIZE]
            for i in range(0, len(master_ids), _BRAND_BATCH_SIZE)
        ]
        aggregated: dict[str, dict[int, list[dict]]] = defaultdict(dict)
        errors: list[str] = []

        def _run(
            dim: BrandFetchDim, batch: list[int]
        ) -> KeyedSliceResult[dict[int, list[dict]]]:
            result = self._fetch_brand_batch(batch, dim, last_sale_time)
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

        records: list[BrandSalesRecord] = []
        for dim in BRAND_FETCH_DIMS:
            records.extend(self._collect_brand_rows(aggregated.get(dim.dim_key(), {}), dim))

        ok = len(errors) == 0
        logger.info(
            "品牌销量拉取完成: 品牌数=%s, 维度数=%s, 总记录数=%s, ok=%s",
            len(master_ids), len(BRAND_FETCH_DIMS), len(records), ok,
        )
        return SourceFetchResult(records=records, ok=ok, errors=errors)
