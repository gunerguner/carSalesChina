import hashlib
import json
import logging
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)

_OVERALL_API_URL = (
    "https://carwebapi.yiche.com/carrankingapi/api/carserialsalestrend/search"
)
_CID = "602"
_SECRET = "DB2560A6EBC65F37A0484295CD4EDD25"
_BRAND_API_URL = (
    "https://mhapi.yiche.com/hcar/h_car/h5/api/v1/ranking/get_master_sales_history"
)
_API_BATCH = 5
_WORKERS = 8


class SaleType:
    """易车 carserialsalestrend 等接口 salesType 参数。"""

    WHOLESALE = 0
    RETAIL = 1
    TERMINAL = 2
    PRODUCTION = 3
    EXPORT = 4


class LevelType:
    """易车 carserialsalestrend 接口 levelType 参数。
    -1 所有轿车；4 新能源；5 纯电（与 total-sales 技术方案一致）。"""

    ALL = -1
    SEDAN = 1
    SUV = 2
    MPV = 3
    NEW_ENERGY = 4
    BEV = 5
    HYBRID = 6


class BrandIsNewEnergy:
    """mhapi /get_master_sales_history 的 isNewEnergy 参数（与 levelType 无关）。"""

    ALL = -1
    NEW_ENERGY = 1
    BEV = 3


@dataclass(frozen=True)
class FetchDim:
    sales_type: int
    time_type: int
    level_type: int
    data_type: str
    date_type: str
    level_label: str


FETCH_DIMS = [
    FetchDim(SaleType.RETAIL, 0, LevelType.ALL, "retail", "monthly", "all"),
    FetchDim(SaleType.RETAIL, 0, LevelType.NEW_ENERGY, "retail", "monthly", "nev"),
    FetchDim(SaleType.RETAIL, 0, LevelType.BEV, "retail", "monthly", "bev"),
    FetchDim(SaleType.PRODUCTION, 0, LevelType.ALL, "production", "monthly", "all"),
    FetchDim(SaleType.PRODUCTION, 0, LevelType.NEW_ENERGY, "production", "monthly", "nev"),
    FetchDim(SaleType.PRODUCTION, 0, LevelType.BEV, "production", "monthly", "bev"),
]


@dataclass(frozen=True)
class BrandDim:
    sale_type_val: int = SaleType.RETAIL
    energy_val: int = BrandIsNewEnergy.ALL
    manu_val: int = -1
    city_id: int = 0
    province_id: int = 0

    def label(self) -> str:
        parts = [f"sale={self.sale_type_val}"]
        if self.energy_val != BrandIsNewEnergy.ALL:
            parts.append(f"energy={self.energy_val}")
        if self.manu_val != -1:
            parts.append(f"manu={self.manu_val}")
        if self.city_id:
            parts.append(f"city={self.city_id}")
        if self.province_id:
            parts.append(f"prov={self.province_id}")
        return "|".join(parts)

    def to_param(self, master_ids: list[int], last_sale_time: str) -> dict:
        p: dict[str, Any] = {
            "masterIds": ",".join(str(i) for i in master_ids),
            "cityId": self.city_id,
            "isNewEnergy": self.energy_val,
            "manu": self.manu_val,
            "saleType": self.sale_type_val,
            "lastSaleTime": last_sale_time,
        }
        if self.province_id:
            p["provinceId"] = self.province_id
        return p


BRAND_FETCH_DIMS = [
    (
        BrandDim(sale_type_val=SaleType.RETAIL, energy_val=BrandIsNewEnergy.ALL),
        "retail",
        "all",
    ),
    (
        BrandDim(sale_type_val=SaleType.RETAIL, energy_val=BrandIsNewEnergy.NEW_ENERGY),
        "retail",
        "nev",
    ),
    (
        BrandDim(sale_type_val=SaleType.RETAIL, energy_val=BrandIsNewEnergy.BEV),
        "retail",
        "bev",
    ),
    (
        BrandDim(sale_type_val=SaleType.WHOLESALE, energy_val=BrandIsNewEnergy.ALL),
        "wholesale",
        "all",
    ),
    (
        BrandDim(sale_type_val=SaleType.PRODUCTION, energy_val=BrandIsNewEnergy.ALL),
        "production",
        "all",
    ),
]


class YicheClient:

    def _sign(self, param: dict, ts: int) -> str:
        param_json = json.dumps(param, separators=(",", ":"), ensure_ascii=False)
        raw = f"cid={_CID}&param={param_json}{_SECRET}{ts}"
        return hashlib.md5(raw.encode()).hexdigest()

    # ---- 总体销量 ----

    def _fetch_overall(
        self, sales_type: int, time_type: int, level_type: int
    ) -> list[dict]:
        params = {
            "app_ver": "",
            "levelType": level_type,
            "timeType": time_type,
            "salesType": sales_type,
        }
        try:
            resp = httpx.get(_OVERALL_API_URL, params=params, timeout=30)
            resp.raise_for_status()
            body = resp.json()
            if body.get("status") != 1:
                logger.warning("易车 API 返回异常: %s", body.get("message"))
                return []
            return body.get("data", [])
        except Exception as e:
            logger.error(
                "易车 API 请求失败 (salesType=%s, timeType=%s, levelType=%s): %s",
                sales_type, time_type, level_type, e,
            )
            return []

    @staticmethod
    def _normalize_overall(raw: dict, dim: FetchDim) -> Optional[dict]:
        sales_num = raw.get("salesNum")
        if sales_num is None:
            return None
        year = raw.get("year")
        month = raw.get("month", 0)
        quarter = raw.get("quarter", 0)
        if dim.date_type == "monthly":
            store_month = month
        elif dim.date_type == "quarterly":
            store_month = quarter
        else:
            store_month = 0
        return {
            "year": year,
            "month": store_month,
            "sales": float(sales_num),
            "data_type": dim.data_type,
            "date_type": dim.date_type,
            "level_type": dim.level_label,
        }

    def fetch_all(self) -> list[dict]:
        all_records = []
        for dim in FETCH_DIMS:
            raw_data = self._fetch_overall(dim.sales_type, dim.time_type, dim.level_type)
            for raw in raw_data:
                normalized = self._normalize_overall(raw, dim)
                if normalized:
                    all_records.append(normalized)
            logger.info(
                "已拉取: salesType=%s, timeType=%s, levelType=%s, 记录数=%s",
                dim.sales_type, dim.time_type, dim.level_type, len(raw_data),
            )
            time.sleep(0.5)
        return all_records

    # ---- 品牌销量 ----

    def _request_brand(self, param: dict) -> dict:
        ts = int(time.time() * 1000)
        param_json = json.dumps(param, separators=(",", ":"), ensure_ascii=False)
        sign = self._sign(param, ts)
        headers = {
            "x-timestamp": str(ts),
            "x-sign": sign,
            "x-platform": "phone",
            "x-longitude": "",
            "x-latitude": "",
            "x-user-guid": str(uuid.uuid4()),
            "x-ip-address": "",
            "x-city-id": str(param.get("cityId", "")),
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
            ),
            "Referer": "https://h5mp.yiche.com/",
        }
        resp = httpx.get(
            _BRAND_API_URL,
            params={"cid": _CID, "param": param_json},
            headers=headers,
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()

    def _fetch_brand_batch(
        self,
        master_ids: list[int],
        dim: BrandDim,
        last_sale_time: str,
    ) -> dict[int, list[dict]]:
        try:
            result = self._request_brand(dim.to_param(master_ids, last_sale_time))
            if str(result.get("status")) != "1":
                return {}
            series_list: list[list[dict]] = result.get("data") or []
            return {
                master_ids[i]: series_list[i]
                for i in range(min(len(master_ids), len(series_list)))
            }
        except Exception:
            return {}

    def fetch_brand_sales(
        self,
        master_ids: list[int],
        last_sale_time: str = "2026-05-01",
    ) -> list[dict]:
        if not master_ids:
            return []

        batches = [
            master_ids[i: i + _API_BATCH]
            for i in range(0, len(master_ids), _API_BATCH)
        ]

        aggregated: dict[str, dict[int, list[dict]]] = {}

        def _run(dim: BrandDim, batch: list[int]) -> tuple[str, dict[int, list[dict]]]:
            return dim.label(), self._fetch_brand_batch(batch, dim, last_sale_time)

        with ThreadPoolExecutor(max_workers=_WORKERS) as executor:
            futures = {
                executor.submit(_run, dim, batch): (dim, batch)
                for dim, _, _ in BRAND_FETCH_DIMS
                for batch in batches
            }
            for future in as_completed(futures):
                label, partial = future.result()
                if label not in aggregated:
                    aggregated[label] = {}
                aggregated[label].update(partial)

        records = []
        for dim, data_type, level_type in BRAND_FETCH_DIMS:
            label = dim.label()
            brand_map = aggregated.get(label, {})
            for master_id, series in brand_map.items():
                for row in series:
                    year = row.get("year")
                    month = row.get("month")
                    num = row.get("num")
                    if year is None or month is None or num is None:
                        continue
                    records.append({
                        "year": year,
                        "month": month,
                        "master_id": master_id,
                        "sales_volume": float(num),
                        "data_type": data_type,
                        "date_type": "monthly",
                        "level_type": level_type,
                    })

        logger.info(
            "品牌销量拉取完成: 品牌数=%s, 维度数=%s, 总记录数=%s",
            len(master_ids), len(BRAND_FETCH_DIMS), len(records),
        )
        return records
