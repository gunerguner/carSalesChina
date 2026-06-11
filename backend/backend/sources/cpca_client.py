import logging
import re
from typing import Any

import akshare as ak
import pandas as pd

from backend.common.types import OriginShareUpsertRow
from backend.sources.fetch_result import SliceResult, SourceFetchResult

logger = logging.getLogger(__name__)


def _parse_month(date_str: str) -> tuple[int | None, int]:
    clean = str(date_str).strip().replace(" ", "")
    year_match = re.search(r"(20\d{2})", clean)
    year = int(year_match.group(1)) if year_match else None

    if year_match:
        tail = clean[year_match.end():]
        month_match = re.search(r"[-年/]?(1[0-2]|0?[1-9])月?", tail)
    else:
        month_match = re.search(r"^(1[0-2]|0?[1-9])月?$", clean)
    if not month_match:
        raise ValueError(f"无法解析月份: {date_str}")
    return year, int(month_match.group(1))


def _try_parse_month(date_str: str) -> tuple[int | None, int | None]:
    try:
        year, month = _parse_month(date_str)
        return year, month
    except ValueError:
        return None, None


def _to_float(value: Any) -> float | None:
    if pd.isna(value):
        return None
    if isinstance(value, str):
        clean = value.replace(",", "").replace("%", "").strip()
        if clean in {"", "-", "--"}:
            return None
        return float(clean)
    return float(value)


def _transform_country(df: pd.DataFrame) -> list[OriginShareUpsertRow]:
    df = df.dropna(subset=["月份"])
    if df.empty:
        return []

    parsed = df["月份"].astype(str).map(_try_parse_month)
    work = df.copy()
    work["year"] = parsed.map(lambda item: item[0])
    work["month"] = parsed.map(lambda item: item[1])
    work = work.dropna(subset=["year", "month"])
    if work.empty:
        return []

    work["year"] = work["year"].astype(int)
    work["month"] = work["month"].astype(int)

    value_cols = [col for col in work.columns if col not in {"月份", "year", "month"}]
    melted = work.melt(
        id_vars=["year", "month"],
        value_vars=value_cols,
        var_name="origin",
        value_name="sales_volume",
    )
    melted["sales_volume"] = melted["sales_volume"].map(_to_float)
    melted = melted.dropna(subset=["sales_volume"])

    return [
        {
            "year": int(row["year"]),
            "month": int(row["month"]),
            "origin": str(row["origin"]),
            "sales_volume": float(row["sales_volume"]),
        }
        for row in melted.to_dict("records")
    ]


def _fetch_country_records() -> SliceResult[list[OriginShareUpsertRow]]:
    try:
        df = ak.car_market_country_cpca()
        return SliceResult(data=_transform_country(df))
    except Exception as e:
        logger.error("获取国别数据失败: %s", e)
        return SliceResult(data=[], error=str(e))


class CpcaClient:
    def get_country_data(self) -> SourceFetchResult:
        result = _fetch_country_records()
        if result.ok:
            logger.info("获取国别数据成功, 记录数=%s", len(result.data))
        return SourceFetchResult(
            records=result.data,
            ok=result.ok,
            errors=[result.error] if result.error else [],
        )
