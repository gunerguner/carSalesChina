"""易车 HTTP 签名、维度常量与纯函数工具。"""

import hashlib
import logging
import time
import uuid
from dataclasses import dataclass

import httpx

from backend.sources.fetch_result import HttpJsonResult

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
_OVERALL_SALE_EXPORT = 4
_OVERALL_LEVEL = {"all": -1, "nev": 4, "bev": 5}

_BRAND_SALE_RETAIL = 1
_BRAND_SALE_EXPORT = 3
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
    + _overall_dims(_OVERALL_SALE_EXPORT, "export")
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
    BrandFetchDim(_BRAND_SALE_EXPORT, _BRAND_ENERGY["all"], "export", "all"),
]
