import logging
from typing import Any

import akshare as ak
import pandas as pd

from backend.sources.base import BaseDataSource

logger = logging.getLogger(__name__)


def _parse_month(date_str: str) -> tuple[int, int]:
    """从 '2025-3月' 或 '3月' 格式解析年月"""
    if '-' in date_str:
        parts = date_str.split('-')
        year = int(parts[0])
        month = int(parts[1].replace('月', ''))
    else:
        month = int(date_str.replace('月', ''))
        year = 2025
    return year, month


def _transform_year_columns(df: pd.DataFrame) -> list[dict[str, Any]]:
    """将列名是年份的 DataFrame 转换为行记录"""
    records = []
    month_col = df.columns[0]
    year_cols = [c for c in df.columns if c != month_col]

    for _, row in df.iterrows():
        month_str = row[month_col]
        if pd.isna(month_str):
            continue
        _, month = _parse_month(str(month_str))

        for year_col in year_cols:
            if '年' not in str(year_col):
                continue
            year = int(str(year_col).replace('年', ''))
            value = row[year_col]
            if pd.notna(value):
                records.append({
                    'year': year,
                    'month': month,
                    'value': float(value)
                })
    return records


def _transform_manufacturer_rank(df: pd.DataFrame) -> list[dict[str, Any]]:
    """转换厂商排名数据"""
    records = []
    for _, row in df.iterrows():
        manufacturer = row['厂商']
        for col in df.columns[1:]:
            col_str = str(col)
            if '年' in col_str and '月' in col_str:
                parts = col_str.replace('年', '-').replace('月', '')
                year, month = parts.split('-')
                value = row[col]
                if pd.notna(value):
                    records.append({
                        'year': int(year),
                        'month': int(month),
                        '品牌名称': manufacturer,
                        '销量': float(value)
                    })
    return records


def _transform_segment(df: pd.DataFrame) -> list[dict[str, Any]]:
    """转换级别细分数据"""
    records = []
    for _, row in df.iterrows():
        month_str = row['月份']
        if pd.isna(month_str):
            continue
        year, month = _parse_month(str(month_str))
        for col in df.columns[1:]:
            value = row[col]
            if pd.notna(value):
                records.append({
                    'year': year,
                    'month': month,
                    '级别': col,
                    '销量': float(value)
                })
    return records


def _transform_country(df: pd.DataFrame) -> list[dict[str, Any]]:
    """转换国别数据"""
    records = []
    for _, row in df.iterrows():
        month_str = row['月份']
        if pd.isna(month_str):
            continue
        year, month = _parse_month(str(month_str))
        for col in df.columns[1:]:
            value = row[col]
            if pd.notna(value):
                records.append({
                    'year': year,
                    'month': month,
                    '国别': col,
                    '销量': float(value)
                })
    return records


class CpcaClient(BaseDataSource):
    def get_monthly_overall(self, date: str = None) -> list[dict[str, Any]]:
        """获取月度整体销量数据"""
        try:
            df = ak.car_market_total_cpca(symbol='狭义乘用车')
            records = _transform_year_columns(df)

            result = []
            for r in records:
                result.append({
                    'year': r['year'],
                    'month': r['month'],
                    '总销量': r['value']
                })

            logger.info(f"获取月度整体数据成功, 记录数={len(result)}")
            return result
        except Exception as e:
            logger.error(f"获取月度整体数据失败: {e}")
            return []

    def get_nev_overall(self) -> list[dict[str, Any]]:
        """获取新能源整体销量数据"""
        try:
            df = ak.car_market_fuel_cpca(symbol='整体市场')
            records = _transform_year_columns(df)

            result = []
            for r in records:
                result.append({
                    'year': r['year'],
                    'month': r['month'],
                    '新能源销量': r['value']
                })

            logger.info(f"获取新能源整体数据成功, 记录数={len(result)}")
            return result
        except Exception as e:
            logger.error(f"获取新能源整体数据失败: {e}")
            return []

    def get_brand_ranking(self, date: str = None) -> list[dict[str, Any]]:
        """获取厂商排名数据"""
        try:
            df = ak.car_market_man_rank_cpca(symbol='狭义乘用车-单月')
            records = _transform_manufacturer_rank(df)

            logger.info(f"获取品牌排行数据成功, 记录数={len(records)}")
            return records
        except Exception as e:
            logger.error(f"获取品牌排行数据失败: {e}")
            return []

    def get_segment_data(self) -> list[dict[str, Any]]:
        """获取级别细分数据"""
        try:
            df = ak.car_market_segment_cpca(symbol='轿车')
            records = _transform_segment(df)

            logger.info(f"获取级别细分数据成功, 记录数={len(records)}")
            return records
        except Exception as e:
            logger.error(f"获取级别细分数据失败: {e}")
            return []

    def get_country_data(self) -> list[dict[str, Any]]:
        """获取国别数据"""
        try:
            df = ak.car_market_country_cpca()
            records = _transform_country(df)

            logger.info(f"获取国别数据成功, 记录数={len(records)}")
            return records
        except Exception as e:
            logger.error(f"获取国别数据失败: {e}")
            return []

    def get_energy_breakdown(self) -> list[dict[str, Any]]:
        """获取能源细分数据"""
        try:
            df = ak.car_market_fuel_cpca(symbol='销量占比-PHEV-BEV')
            records = _transform_year_columns(df)

            result = []
            for r in records:
                result.append({
                    'year': r['year'],
                    'month': r['month'],
                    '能源类型': '新能源',
                    '销量': r['value']
                })

            logger.info(f"获取能源细分数据成功, 记录数={len(result)}")
            return result
        except Exception as e:
            logger.error(f"获取能源细分数据失败: {e}")
            return []

    def get_factory_ranking(self, date: str = None) -> list[dict[str, Any]]:
        return self.get_brand_ranking(date)
