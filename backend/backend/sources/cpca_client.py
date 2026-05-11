import logging
import re
from typing import Any

import akshare as ak
import pandas as pd

from backend.sources.base import BaseDataSource

logger = logging.getLogger(__name__)

DATA_TYPE_TO_TOTAL_INDICATOR = {
    "retail": "零售",
    "wholesale": "批发",
    "production": "产量",
}

DATA_TYPE_TO_BRAND_INDICATOR = {
    "retail": "零售",
    "wholesale": "批发",
}


def _parse_month(date_str: str) -> tuple[int | None, int]:
    """从 '2025-3月'、'2025年3月'、'3月' 等格式解析年月。"""
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


def _parse_year_column(column: Any) -> int | None:
    match = re.search(r"(20\d{2})", str(column))
    return int(match.group(1)) if match else None


def _to_float(value: Any) -> float | None:
    if pd.isna(value):
        return None
    if isinstance(value, str):
        clean = value.replace(",", "").replace("%", "").strip()
        if clean in {"", "-", "--"}:
            return None
        return float(clean)
    return float(value)


def _filter_records(records: list[dict[str, Any]], date: str | None = None) -> list[dict[str, Any]]:
    if not date:
        return records
    year = int(date[:4])
    month = int(date[4:6])
    return [r for r in records if r.get("year") == year and r.get("month") == month]


def _transform_year_columns(df: pd.DataFrame) -> list[dict[str, Any]]:
    """将列名是年份的 DataFrame 转换为行记录。"""
    records = []
    if df.empty:
        return records

    month_col = df.columns[0]
    year_cols = [c for c in df.columns if c != month_col]

    for _, row in df.iterrows():
        month_str = row[month_col]
        if pd.isna(month_str):
            continue
        row_year, month = _parse_month(str(month_str))

        for year_col in year_cols:
            col_year = _parse_year_column(year_col)
            year = col_year or row_year
            if not year:
                continue
            value = _to_float(row[year_col])
            if value is not None:
                records.append({"year": year, "month": month, "value": value})
    return records


def _transform_manufacturer_rank(df: pd.DataFrame) -> list[dict[str, Any]]:
    """转换厂商排名数据。"""
    records = []
    if df.empty:
        return records

    manufacturer_col = "厂商" if "厂商" in df.columns else df.columns[0]
    for _, row in df.iterrows():
        manufacturer = str(row[manufacturer_col]).strip()
        if not manufacturer or manufacturer == "nan":
            continue
        for col in df.columns:
            if col == manufacturer_col:
                continue
            year = _parse_year_column(col)
            if not year:
                continue
            _, month = _parse_month(str(col))
            value = _to_float(row[col])
            if value is not None:
                records.append({
                    "year": year,
                    "month": month,
                    "品牌名称": manufacturer,
                    "销量": value,
                })
    return records


def _transform_segment(df: pd.DataFrame) -> list[dict[str, Any]]:
    """转换级别细分数据。"""
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
                records.append({"year": year, "month": month, "级别": col, "销量": value})
    return records


def _transform_country(df: pd.DataFrame) -> list[dict[str, Any]]:
    """转换国别数据。"""
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


class CpcaClient(BaseDataSource):
    def get_monthly_overall(self, date: str = None, data_type: str = "retail") -> list[dict[str, Any]]:
        """获取月度整体销量/批发/产量数据。"""
        indicator = DATA_TYPE_TO_TOTAL_INDICATOR.get(data_type)
        if not indicator:
            raise ValueError(f"不支持的总体数据类型: {data_type}")

        try:
            df = ak.car_market_total_cpca(symbol="狭义乘用车", indicator=indicator)
            records = _transform_year_columns(df)
            result = []
            for r in _filter_records(records, date):
                result.append({
                    "year": r["year"],
                    "month": r["month"],
                    "总销量": r["value"],
                    "data_type": data_type,
                })

            logger.info("获取月度整体数据成功, data_type=%s, 记录数=%s", data_type, len(result))
            return result
        except Exception as e:
            logger.error("获取月度整体数据失败, data_type=%s: %s", data_type, e)
            return []

    def get_nev_overall(self, date: str = None) -> list[dict[str, Any]]:
        """获取新能源整体销量数据。"""
        try:
            df = ak.car_market_fuel_cpca(symbol="整体市场")
            records = _transform_year_columns(df)

            result = []
            for r in _filter_records(records, date):
                result.append({
                    "year": r["year"],
                    "month": r["month"],
                    "新能源销量": r["value"],
                    "data_type": "retail",
                })

            logger.info("获取新能源整体数据成功, 记录数=%s", len(result))
            return result
        except Exception as e:
            logger.error("获取新能源整体数据失败: %s", e)
            return []

    def get_brand_ranking(self, date: str = None, data_type: str = "retail") -> list[dict[str, Any]]:
        """获取厂商月度排名数据。乘联会该接口仅支持零售和批发。"""
        indicator = DATA_TYPE_TO_BRAND_INDICATOR.get(data_type)
        if not indicator:
            logger.warning("厂商排名接口不支持 data_type=%s", data_type)
            return []

        try:
            df = ak.car_market_man_rank_cpca(symbol="狭义乘用车-单月", indicator=indicator)
            records = _transform_manufacturer_rank(df)
            result = []
            for r in _filter_records(records, date):
                r["data_type"] = data_type
                result.append(r)

            logger.info("获取品牌排行数据成功, data_type=%s, 记录数=%s", data_type, len(result))
            return result
        except Exception as e:
            logger.error("获取品牌排行数据失败, data_type=%s: %s", data_type, e)
            return []

    def get_segment_data(self) -> list[dict[str, Any]]:
        """获取级别细分数据。"""
        try:
            df = ak.car_market_segment_cpca(symbol="轿车")
            records = _transform_segment(df)

            logger.info("获取级别细分数据成功, 记录数=%s", len(records))
            return records
        except Exception as e:
            logger.error("获取级别细分数据失败: %s", e)
            return []

    def get_country_data(self, data_type: str = "retail") -> list[dict[str, Any]]:
        """获取国别数据。"""
        try:
            df = ak.car_market_country_cpca()
            records = _transform_country(df)

            result = []
            for r in records:
                result.append({
                    "year": r["year"],
                    "month": r["month"],
                    "origin": r["国别"],
                    "sales_volume": r["销量"],
                    "data_type": data_type,
                })

            logger.info("获取国别数据成功, data_type=%s, 记录数=%s", data_type, len(result))
            return result
        except Exception as e:
            logger.error("获取国别数据失败: %s", e)
            return []

    def get_energy_breakdown(self) -> list[dict[str, Any]]:
        """获取能源细分数据。"""
        try:
            df = ak.car_market_fuel_cpca(symbol="销量占比-PHEV-BEV")
            records = _transform_year_columns(df)

            result = []
            for r in records:
                result.append({
                    "year": r["year"],
                    "month": r["month"],
                    "能源类型": "新能源",
                    "销量": r["value"],
                })

            logger.info("获取能源细分数据成功, 记录数=%s", len(result))
            return result
        except Exception as e:
            logger.error("获取能源细分数据失败: %s", e)
            return []

    def get_factory_ranking(self, date: str = None) -> list[dict[str, Any]]:
        return self.get_brand_ranking(date)
