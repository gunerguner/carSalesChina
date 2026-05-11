import logging
from datetime import datetime
from pathlib import Path
from typing import Iterable

import yaml
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.orm import Session

from backend.models.brand import BrandMeta, BrandSales
from backend.models.log import CollectionLog
from backend.models.overall import SalesData
from backend.sources.cpca_client import CpcaClient

logger = logging.getLogger(__name__)

client = CpcaClient()
DEFAULT_IMPORT_DATA_TYPES = ("retail", "wholesale", "production")
BRAND_DATA_TYPES = ("retail", "wholesale")

# 加载品牌国别配置
_META_DATA_PATH = Path(__file__).parent.parent / "meta_data.yaml"
with open(_META_DATA_PATH, "r", encoding="utf-8") as f:
    _META_DATA = yaml.safe_load(f)

ORIGIN_MAP: dict[str, list[str]] = _META_DATA.get("brand_origins", {})


def _get_origin(brand_name: str) -> str:
    for origin, brands in ORIGIN_MAP.items():
        if any(brand in brand_name for brand in brands):
            return origin
    return "其他"


def _month_key(year: int, month: int) -> tuple[int, int]:
    return year, month


def _is_in_range(record: dict, start_year: int, start_month: int, end_year: int, end_month: int) -> bool:
    key = _month_key(record["year"], record["month"])
    return _month_key(start_year, start_month) <= key <= _month_key(end_year, end_month)


def _filter_range(records: Iterable[dict], start_year: int, start_month: int, end_year: int, end_month: int) -> list[dict]:
    return [r for r in records if _is_in_range(r, start_year, start_month, end_year, end_month)]


def _merge_retail_energy_fields(overall_records: list[dict], nev_records: list[dict]) -> list[dict]:
    """把 akshare 新能源总体数据合并进零售总体数据。"""
    nev_by_month = {(r["year"], r["month"]): r.get("新能源销量") for r in nev_records}
    for rec in overall_records:
        if rec.get("data_type") != "retail":
            continue
        nev_sales = nev_by_month.get((rec["year"], rec["month"]))
        total_sales = rec.get("总销量") or 0
        if nev_sales is not None:
            rec["新能源销量"] = nev_sales
            rec["燃油销量"] = max(total_sales - nev_sales, 0)
    return overall_records


def _add_brand_growth(records: list[dict]) -> list[dict]:
    """按品牌和 data_type 补充同比/环比。"""
    by_key = {(r["品牌名称"], r.get("data_type", "retail"), r["year"], r["month"]): r for r in records}
    for rec in records:
        brand_name = rec["品牌名称"]
        data_type = rec.get("data_type", "retail")
        year = rec["year"]
        month = rec["month"]
        current = rec.get("销量") or 0
        prev_month_year = year if month > 1 else year - 1
        prev_month = month - 1 if month > 1 else 12
        prev_month_rec = by_key.get((brand_name, data_type, prev_month_year, prev_month))
        prev_year_rec = by_key.get((brand_name, data_type, year - 1, month))
        if prev_month_rec and prev_month_rec.get("销量"):
            rec["环比"] = (current - prev_month_rec["销量"]) / prev_month_rec["销量"] * 100
        if prev_year_rec and prev_year_rec.get("销量"):
            rec["同比"] = (current - prev_year_rec["销量"]) / prev_year_rec["销量"] * 100
    return records


def upsert_brand_meta(db: Session, brand_names: Iterable[str]) -> int:
    """批量插入/更新品牌元数据（独立方法，可被单独调用）。"""
    count = 0
    for brand_name in sorted(set(brand_names)):
        stmt = insert(BrandMeta).values(
            brand_name=brand_name,
            origin=_get_origin(brand_name),
        )
        stmt = stmt.on_duplicate_key_update(origin=stmt.inserted.origin)
        db.execute(stmt)
        count += 1
    db.commit()
    logger.info("品牌元数据更新完成: %s 条", count)
    return count


def _upsert_overall(db: Session, records: list[dict]) -> int:
    count = 0
    for rec in records:
        stmt = insert(SalesData).values(
            year=rec["year"],
            month=rec["month"],
            total_sales=rec.get("总销量"),
            nev_sales=rec.get("新能源销量"),
            ice_sales=rec.get("燃油销量"),
            bev_sales=rec.get("纯电销量"),
            phev_sales=rec.get("插混销量"),
            hybrid_sales=rec.get("混动销量"),
            data_type=rec.get("data_type", "retail"),
        )
        stmt = stmt.on_duplicate_key_update(
            total_sales=stmt.inserted.total_sales,
            nev_sales=stmt.inserted.nev_sales,
            ice_sales=stmt.inserted.ice_sales,
            bev_sales=stmt.inserted.bev_sales,
            phev_sales=stmt.inserted.phev_sales,
            hybrid_sales=stmt.inserted.hybrid_sales,
        )
        db.execute(stmt)
        count += 1
    db.commit()
    return count


def _upsert_brand(db: Session, records: list[dict]) -> int:
    count = 0
    for rec in records:
        brand_name = rec.get("品牌名称", "")
        if not brand_name:
            continue
        stmt = insert(BrandSales).values(
            year=rec["year"],
            month=rec["month"],
            brand_name=brand_name,
            sales_volume=rec.get("销量"),
            yoy_growth=rec.get("同比"),
            mom_growth=rec.get("环比"),
            data_type=rec.get("data_type", "retail"),
        )
        stmt = stmt.on_duplicate_key_update(
            sales_volume=stmt.inserted.sales_volume,
            yoy_growth=stmt.inserted.yoy_growth,
            mom_growth=stmt.inserted.mom_growth,
        )
        db.execute(stmt)
        count += 1
    db.commit()
    return count


def import_monthly_data(db: Session, year: int, month: int, data_types: Iterable[str] = DEFAULT_IMPORT_DATA_TYPES) -> dict:
    data_types = tuple(data_types)
    date_str = f"{year}{month:02d}"
    log = CollectionLog(
        task_type="market",
        status="pending",
        started_at=datetime.now(),
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    total_count = 0
    try:
        overall_records = []
        brand_records = []
        nev_records = client.get_nev_overall(date_str)
        for data_type in data_types:
            monthly_overall = client.get_monthly_overall(date_str, data_type=data_type)
            overall_records.extend(monthly_overall)
            if data_type in BRAND_DATA_TYPES:
                brand_records.extend(client.get_brand_ranking(date_str, data_type=data_type))

        _merge_retail_energy_fields(overall_records, nev_records)
        brand_records = _add_brand_growth(brand_records)

        total_count += _upsert_overall(db, overall_records)
        total_count += _upsert_brand(db, brand_records)

        log.status = "success"
        log.records_count = total_count
        log.finished_at = datetime.now()
        db.commit()
        logger.info("数据采集完成: %s-%s, 入库 %s 条", year, month, total_count)
    except Exception as e:
        log.status = "failed"
        log.error_message = str(e)
        log.finished_at = datetime.now()
        db.commit()
        logger.error("数据采集失败: %s-%s: %s", year, month, e)
        raise

    return {"year": year, "month": month, "records_count": total_count, "status": "success"}


def import_cpca_range(
    db: Session,
    start_year: int = 2024,
    start_month: int = 1,
    end_year: int = 2026,
    end_month: int = 12,
    data_types: Iterable[str] = DEFAULT_IMPORT_DATA_TYPES,
) -> dict:
    """批量导入 2024-2026 月度总体和品牌数据，避免每个月重复请求 akshare。"""
    data_types = tuple(data_types)
    log = CollectionLog(
        task_type="cpca_history",
        status="pending",
        started_at=datetime.now(),
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    try:
        overall_records = []
        brand_records = []
        nev_records = _filter_range(client.get_nev_overall(), start_year, start_month, end_year, end_month)
        for data_type in data_types:
            records = client.get_monthly_overall(data_type=data_type)
            overall_records.extend(_filter_range(records, start_year, start_month, end_year, end_month))
            if data_type in BRAND_DATA_TYPES:
                brand_records.extend(_filter_range(
                    client.get_brand_ranking(data_type=data_type),
                    start_year,
                    start_month,
                    end_year,
                    end_month,
                ))

        _merge_retail_energy_fields(overall_records, nev_records)
        brand_records = _add_brand_growth(brand_records)

        overall_count = _upsert_overall(db, overall_records)
        brand_count = _upsert_brand(db, brand_records)
        total_count = overall_count + brand_count

        log.status = "success"
        log.records_count = total_count
        log.finished_at = datetime.now()
        db.commit()
        logger.info(
            "CPCA 历史数据采集完成: %s-%02d 至 %s-%02d, 总体 %s 条, 品牌 %s 条",
            start_year,
            start_month,
            end_year,
            end_month,
            overall_count,
            brand_count,
        )
        return {
            "start_year": start_year,
            "start_month": start_month,
            "end_year": end_year,
            "end_month": end_month,
            "data_types": list(data_types),
            "overall_count": overall_count,
            "brand_count": brand_count,
            "records_count": total_count,
            "status": "success",
        }
    except Exception as e:
        log.status = "failed"
        log.error_message = str(e)
        log.finished_at = datetime.now()
        db.commit()
        logger.error("CPCA 历史数据采集失败: %s", e)
        raise


def import_history(db: Session, months: int = 36) -> list[dict]:
    results = []
    now = datetime.now()
    for i in range(months):
        y = now.year - ((now.month - 1 - i) // 12)
        m = (now.month - 1 - i) % 12 + 1
        if m <= 0:
            m += 12
            y -= 1
        try:
            result = import_monthly_data(db, y, m)
            results.append(result)
        except Exception:
            results.append({"year": y, "month": m, "status": "failed"})
    return results
