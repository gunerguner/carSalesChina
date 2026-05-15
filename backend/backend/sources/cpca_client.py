import logging
import re
from typing import Any

import akshare as ak
import pandas as pd

from backend.sources.fetch_result import SourceFetchResult

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


def _to_float(value: Any) -> float | None:
    if pd.isna(value):
        return None
    if isinstance(value, str):
        clean = value.replace(",", "").replace("%", "").strip()
        if clean in {"", "-", "--"}:
            return None
        return float(clean)
    return float(value)


def _transform_country(df: pd.DataFrame) -> list[dict[str, Any]]:
    records = []
    for _, row in df.iterrows():
        month_str = row["月份"]
        if pd.isna(month_str):
            continue
        year, month = _parse_month(str(month_str))
        if not year:
            continue
        for col in df.columns[1:]:
            value = _to_float(row[col])
            if value is not None:
                records.append({"year": year, "month": month, "国别": col, "销量": value})
    return records


class CpcaClient:
    def get_country_data(self) -> SourceFetchResult:
        try:
            df = ak.car_market_country_cpca()
            records = _transform_country(df)

            result = []
            for r in records:
                result.append(
                    {
                        "year": r["year"],
                        "month": r["month"],
                        "origin": r["国别"],
                        "sales_volume": r["销量"],
                    }
                )

            logger.info("获取国别数据成功, 记录数=%s", len(result))
            return SourceFetchResult(records=result, ok=True)
        except Exception as e:
            logger.error("获取国别数据失败: %s", e)
            return SourceFetchResult(records=[], ok=False, errors=[str(e)])
