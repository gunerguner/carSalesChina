import logging
import time
from typing import Optional

import requests

logger = logging.getLogger(__name__)

YICHE_API_URL = (
    "https://carwebapi.yiche.com/carrankingapi/api/carserialsalestrend/search"
)

FETCH_COMBINATIONS = [
    (1, 0, -1, "retail", "monthly", "all"),
    (1, 0, 4, "retail", "monthly", "nev"),
    (1, 0, 5, "retail", "monthly", "bev"),
    (1, 1, -1, "retail", "quarterly", "all"),
    (1, 1, 4, "retail", "quarterly", "nev"),
    (1, 1, 5, "retail", "quarterly", "bev"),
    (1, 2, -1, "retail", "yearly", "all"),
    (1, 2, 4, "retail", "yearly", "nev"),
    (1, 2, 5, "retail", "yearly", "bev"),
    (3, 0, -1, "production", "monthly", "all"),
    (3, 0, 4, "production", "monthly", "nev"),
    (3, 0, 5, "production", "monthly", "bev"),
    (3, 1, -1, "production", "quarterly", "all"),
    (3, 1, 4, "production", "quarterly", "nev"),
    (3, 1, 5, "production", "quarterly", "bev"),
    (3, 2, -1, "production", "yearly", "all"),
    (3, 2, 4, "production", "yearly", "nev"),
    (3, 2, 5, "production", "yearly", "bev"),
]


class YicheClient:

    def __init__(self, base_url: str = YICHE_API_URL):
        self.base_url = base_url

    def _fetch(
        self, sales_type: int, time_type: int, level_type: int
    ) -> list[dict]:
        params = {
            "app_ver": "",
            "levelType": level_type,
            "timeType": time_type,
            "salesType": sales_type,
        }
        try:
            resp = requests.get(self.base_url, params=params, timeout=30)
            resp.raise_for_status()
            body = resp.json()
            if body.get("status") != 1:
                logger.warning("易车 API 返回异常: %s", body.get("message"))
                return []
            return body.get("data", [])
        except Exception as e:
            logger.error(
                "易车 API 请求失败 (salesType=%s, timeType=%s, levelType=%s): %s",
                sales_type,
                time_type,
                level_type,
                e,
            )
            return []

    def _normalize(
        self,
        raw: dict,
        data_type: str,
        date_type: str,
        level_type: str,
    ) -> Optional[dict]:
        sales_num = raw.get("salesNum")
        if sales_num is None:
            return None

        year = raw.get("year")
        month = raw.get("month", 0)
        quarter = raw.get("quarter", 0)

        if date_type == "monthly":
            store_month = month
        elif date_type == "quarterly":
            store_month = quarter
        else:
            store_month = 0

        return {
            "year": year,
            "month": store_month,
            "sales": float(sales_num),
            "data_type": data_type,
            "date_type": date_type,
            "level_type": level_type,
        }

    def fetch_all(self) -> list[dict]:
        all_records = []
        for (
            sales_type,
            time_type,
            level_type,
            data_type,
            date_type,
            lvl_type,
        ) in FETCH_COMBINATIONS:
            raw_data = self._fetch(sales_type, time_type, level_type)
            for raw in raw_data:
                normalized = self._normalize(
                    raw, data_type, date_type, lvl_type
                )
                if normalized:
                    all_records.append(normalized)
            logger.info(
                "已拉取: salesType=%s, timeType=%s, levelType=%s, 记录数=%s",
                sales_type,
                time_type,
                level_type,
                len(raw_data),
            )
            time.sleep(0.5)
        return all_records