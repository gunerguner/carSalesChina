import logging
from typing import Any

import akshare as ak
import pandas as pd

from backend.sources.base import BaseDataSource

logger = logging.getLogger(__name__)


def _fillna_and_convert(df: pd.DataFrame) -> pd.DataFrame:
    df = df.fillna(0)
    for col in df.columns:
        if df[col].dtype == object:
            try:
                df[col] = pd.to_numeric(df[col])
            except (ValueError, TypeError):
                pass
    return df


class CpcaClient(BaseDataSource):
    def get_monthly_overall(self, date: str) -> list[dict[str, Any]]:
        try:
            df = ak.stock_car_cPCA(date=date)
            df = _fillna_and_convert(df)
            records = df.to_dict(orient="records")
            logger.info(f"获取月度整体数据成功, date={date}, 记录数={len(records)}")
            return records
        except Exception as e:
            logger.error(f"获取月度整体数据失败, date={date}: {e}")
            return []

    def get_energy_breakdown(self) -> list[dict[str, Any]]:
        try:
            df = ak.energy_car_sale()
            df = _fillna_and_convert(df)
            records = df.to_dict(orient="records")
            logger.info(f"获取能源细分数据成功, 记录数={len(records)}")
            return records
        except Exception as e:
            logger.error(f"获取能源细分数据失败: {e}")
            return []

    def get_brand_ranking(self, date: str) -> list[dict[str, Any]]:
        try:
            df = ak.stock_car_sale_rank_cPCA(date=date)
            df = _fillna_and_convert(df)
            records = df.to_dict(orient="records")
            logger.info(f"获取品牌排行数据成功, date={date}, 记录数={len(records)}")
            return records
        except Exception as e:
            logger.error(f"获取品牌排行数据失败, date={date}: {e}")
            return []

    def get_segment_data(self) -> list[dict[str, Any]]:
        try:
            df = ak.stock_car_market_detail_cPCA()
            df = _fillna_and_convert(df)
            records = df.to_dict(orient="records")
            logger.info(f"获取级别细分数据成功, 记录数={len(records)}")
            return records
        except Exception as e:
            logger.error(f"获取级别细分数据失败: {e}")
            return []

    def get_factory_ranking(self, date: str) -> list[dict[str, Any]]:
        try:
            df = ak.stock_car_factory_rank_cPCA(date=date)
            df = _fillna_and_convert(df)
            records = df.to_dict(orient="records")
            logger.info(f"获取厂商排行数据成功, date={date}, 记录数={len(records)}")
            return records
        except Exception as e:
            logger.error(f"获取厂商排行数据失败, date={date}: {e}")
            return []