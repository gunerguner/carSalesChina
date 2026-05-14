import hashlib
import json
import logging
import time
import uuid
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any, Optional

import httpx

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


def _md5_sign(param_json: str, ts: int) -> str:
    """易车 API MD5 签名：cid=&param={json}{SECRET}{ts}。"""
    raw = f"cid={_CID}&param={param_json}{_SECRET}{ts}"
    return hashlib.md5(raw.encode()).hexdigest()


# ---- 总体销量接口（carserialsalestrend）枚举 ----


class OverallSaleType:
    """carserialsalestrend 接口 salesType 参数。
    注意：3=产量，4=出口；与品牌接口顺序不同。"""

    WHOLESALE = 0
    RETAIL = 1
    TERMINAL = 2
    PRODUCTION = 3  # 产量（overall 接口 3=产量，对应品牌接口的 4）
    EXPORT = 4


class OverallLevelType:
    """carserialsalestrend 接口 levelType 参数。"""

    ALL = -1
    SEDAN = 1
    SUV = 2
    MPV = 3
    NEW_ENERGY = 4
    BEV = 5
    HYBRID = 6


# ---- 品牌销量接口（get_master_sales_history）枚举 ----


class BrandSaleType:
    """get_master_sales_history 接口 saleType 参数。
    注意：3=出口，4=产量；与总体接口顺序不同。"""

    WHOLESALE = 0
    RETAIL = 1
    TERMINAL = 2
    EXPORT = 3      # 出口（brand 接口 3=出口，对应总体接口的 4）
    PRODUCTION = 4  # 产量（brand 接口 4=产量，对应总体接口的 3）


class BrandEnergyType:
    """get_master_sales_history 接口 isNewEnergy 参数。"""

    ALL = -1
    NEW_ENERGY = 1
    FUEL = 2
    BEV = 3
    PHEV = 4
    EXTENDED_RANGE = 5


# ---- 总体销量维度定义 ----


@dataclass(frozen=True)
class OverallFetchDim:
    sale_type: int    # OverallSaleType 枚举值
    time_type: int    # 0=月度, 1=季度, 2=年度
    level_type: int   # OverallLevelType 枚举值
    data_type: str    # 入库 data_type
    date_type: str    # 入库 date_type
    level_label: str  # 入库 level_type


OVERALL_FETCH_DIMS = [
    OverallFetchDim(OverallSaleType.RETAIL, 0, OverallLevelType.ALL, "retail", "monthly", "all"),
    OverallFetchDim(OverallSaleType.RETAIL, 0, OverallLevelType.NEW_ENERGY, "retail", "monthly", "nev"),
    OverallFetchDim(OverallSaleType.RETAIL, 0, OverallLevelType.BEV, "retail", "monthly", "bev"),
    OverallFetchDim(OverallSaleType.PRODUCTION, 0, OverallLevelType.ALL, "production", "monthly", "all"),
    OverallFetchDim(OverallSaleType.PRODUCTION, 0, OverallLevelType.NEW_ENERGY, "production", "monthly", "nev"),
    OverallFetchDim(OverallSaleType.PRODUCTION, 0, OverallLevelType.BEV, "production", "monthly", "bev"),
]


# ---- 品牌销量维度定义 ----


@dataclass(frozen=True)
class BrandQueryParam:
    """品牌销量 API 请求参数（不含 masterIds 和 lastSaleTime）。"""

    sale_type: int = BrandSaleType.RETAIL
    energy_type: int = BrandEnergyType.ALL
    manu_type: int = -1
    city_id: int = 0
    province_id: int = 0

    def label(self) -> str:
        parts = [f"sale={self.sale_type}"]
        if self.energy_type != BrandEnergyType.ALL:
            parts.append(f"energy={self.energy_type}")
        if self.manu_type != -1:
            parts.append(f"manu={self.manu_type}")
        if self.city_id:
            parts.append(f"city={self.city_id}")
        if self.province_id:
            parts.append(f"prov={self.province_id}")
        return "|".join(parts)

    def to_request_param(self, master_ids: list[int], last_sale_time: str) -> dict:
        p: dict[str, Any] = {
            "masterIds": ",".join(str(i) for i in master_ids),
            "cityId": self.city_id,
            "isNewEnergy": self.energy_type,
            "manu": self.manu_type,
            "saleType": self.sale_type,
            "lastSaleTime": last_sale_time,
        }
        if self.province_id:
            p["provinceId"] = self.province_id
        return p


@dataclass(frozen=True)
class BrandFetchDim:
    query_param: BrandQueryParam
    data_type: str    # 入库 data_type
    level_label: str  # 入库 level_type

    def label(self) -> str:
        return self.query_param.label()


BRAND_FETCH_DIMS = [
    BrandFetchDim(
        query_param=BrandQueryParam(sale_type=BrandSaleType.RETAIL, energy_type=BrandEnergyType.ALL),
        data_type="retail",
        level_label="all",
    ),
    BrandFetchDim(
        query_param=BrandQueryParam(sale_type=BrandSaleType.RETAIL, energy_type=BrandEnergyType.NEW_ENERGY),
        data_type="retail",
        level_label="nev",
    ),
    BrandFetchDim(
        query_param=BrandQueryParam(sale_type=BrandSaleType.RETAIL, energy_type=BrandEnergyType.BEV),
        data_type="retail",
        level_label="bev",
    ),
    BrandFetchDim(
        query_param=BrandQueryParam(sale_type=BrandSaleType.WHOLESALE, energy_type=BrandEnergyType.ALL),
        data_type="wholesale",
        level_label="all",
    ),
    BrandFetchDim(
        query_param=BrandQueryParam(sale_type=BrandSaleType.PRODUCTION, energy_type=BrandEnergyType.ALL),
        data_type="production",
        level_label="all",
    ),
]


# ---- 客户端 ----


class YicheOverallClient:
    """易车总体销量客户端（carserialsalestrend 接口）。"""

    def _fetch_overall(self, sale_type: int, time_type: int, level_type: int) -> list[dict]:
        params = {
            "app_ver": "",
            "levelType": level_type,
            "timeType": time_type,
            "salesType": sale_type,
        }
        try:
            resp = httpx.get(_OVERALL_API_URL, params=params, timeout=30)
            resp.raise_for_status()
            body = resp.json()
            if body.get("status") != 1:
                logger.warning("易车总体 API 返回异常: %s", body.get("message"))
                return []
            return body.get("data", [])
        except Exception as e:
            logger.error(
                "易车总体 API 请求失败 (saleType=%s, timeType=%s, levelType=%s): %s",
                sale_type, time_type, level_type, e,
            )
            return []

    @staticmethod
    def _normalize_overall_row(raw: dict, dim: OverallFetchDim) -> Optional[dict]:
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

    def fetch_overall_sales(self) -> list[dict]:
        """拉取总体销量，返回标准化记录列表。"""
        records = []
        for dim in OVERALL_FETCH_DIMS:
            raw_data = self._fetch_overall(dim.sale_type, dim.time_type, dim.level_type)
            for raw in raw_data:
                normalized = self._normalize_overall_row(raw, dim)
                if normalized:
                    records.append(normalized)
            logger.info(
                "总体销量已拉取: saleType=%s, timeType=%s, levelType=%s, 记录数=%s",
                dim.sale_type, dim.time_type, dim.level_type, len(raw_data),
            )
            time.sleep(0.5)
        return records


class YicheBrandClient:
    """易车品牌销量客户端（get_master_sales_history 接口）。"""

    def _request_brand(self, param: dict) -> dict:
        ts = int(time.time() * 1000)
        param_json = json.dumps(param, separators=(",", ":"), ensure_ascii=False)
        sign = _md5_sign(param_json, ts)
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
        dim: BrandFetchDim,
        last_sale_time: str,
    ) -> dict[int, list[dict]]:
        try:
            result = self._request_brand(
                dim.query_param.to_request_param(master_ids, last_sale_time)
            )
            if str(result.get("status")) != "1":
                return {}
            series_list: list[list[dict]] = result.get("data") or []
            return {
                master_ids[i]: series_list[i]
                for i in range(min(len(master_ids), len(series_list)))
            }
        except Exception as e:
            logger.warning(
                "品牌销量批量拉取失败: dim=%s, batch=%s, err=%s", dim.label(), master_ids, e
            )
            return {}

    @staticmethod
    def _chunked_ids(master_ids: list[int], batch_size: int) -> list[list[int]]:
        return [master_ids[i: i + batch_size] for i in range(0, len(master_ids), batch_size)]

    @staticmethod
    def _normalize_brand_row(
        row: dict,
        master_id: int,
        data_type: str,
        level_label: str,
    ) -> Optional[dict]:
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

    def fetch_brand_sales(
        self,
        master_ids: list[int],
        last_sale_time: str = "2026-05-01",
    ) -> list[dict]:
        """并发拉取所有品牌的各维度销量数据。"""
        if not master_ids:
            return []

        batches = self._chunked_ids(master_ids, _BRAND_BATCH_SIZE)
        aggregated: dict[str, dict[int, list[dict]]] = defaultdict(dict)

        def _run(dim: BrandFetchDim, batch: list[int]) -> tuple[str, dict[int, list[dict]]]:
            return dim.label(), self._fetch_brand_batch(batch, dim, last_sale_time)

        with ThreadPoolExecutor(max_workers=_BRAND_WORKERS) as executor:
            futures = {
                executor.submit(_run, dim, batch): (dim, batch)
                for dim in BRAND_FETCH_DIMS
                for batch in batches
            }
            for future in as_completed(futures):
                label, partial = future.result()
                aggregated[label].update(partial)

        records = []
        for dim in BRAND_FETCH_DIMS:
            label = dim.label()
            brand_map = aggregated.get(label, {})
            for master_id, series in brand_map.items():
                for row in series:
                    normalized = self._normalize_brand_row(
                        row=row,
                        master_id=master_id,
                        data_type=dim.data_type,
                        level_label=dim.level_label,
                    )
                    if normalized:
                        records.append(normalized)

        logger.info(
            "品牌销量拉取完成: 品牌数=%s, 维度数=%s, 总记录数=%s",
            len(master_ids), len(BRAND_FETCH_DIMS), len(records),
        )
        return records


class YicheClient(YicheOverallClient, YicheBrandClient):
    """易车 API 聚合客户端，向后兼容原有调用方式。"""

    def fetch_all(self) -> list[dict]:
        return self.fetch_overall_sales()
