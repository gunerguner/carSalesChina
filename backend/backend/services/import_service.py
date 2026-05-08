import logging
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.dialects.mysql import insert

from backend.models.overall import SalesData
from backend.models.brand import BrandSales
from backend.models.log import CollectionLog
from backend.sources.cpca_client import CpcaClient

logger = logging.getLogger(__name__)

client = CpcaClient()


def _upsert_overall(db: Session, records: list[dict], year: int, month: int) -> int:
    count = 0
    for rec in records:
        stmt = insert(SalesData).values(
            year=year,
            month=month,
            total_sales=rec.get("总销量", 0),
            nev_sales=rec.get("新能源销量", 0),
            ice_sales=rec.get("燃油销量", 0),
            bev_sales=rec.get("纯电销量", 0),
            phev_sales=rec.get("插混销量", 0),
            hybrid_sales=rec.get("混动销量", 0),
            data_type="retail",
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


def _upsert_brand(db: Session, records: list[dict], year: int, month: int) -> int:
    count = 0
    for rec in records:
        brand_name = rec.get("品牌名称", "")
        if not brand_name:
            continue
        stmt = insert(BrandSales).values(
            year=year,
            month=month,
            brand_name=brand_name,
            sales_volume=rec.get("销量", 0),
            yoy_growth=rec.get("同比", 0),
            mom_growth=rec.get("环比", 0),
            data_type="retail",
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


def import_monthly_data(db: Session, year: int, month: int) -> dict:
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
        overall_records = client.get_monthly_overall(date_str)
        overall_count = _upsert_overall(db, overall_records, year, month)
        total_count += overall_count

        brand_records = client.get_brand_ranking(date_str)
        brand_count = _upsert_brand(db, brand_records, year, month)
        total_count += brand_count

        log.status = "success"
        log.records_count = total_count
        log.finished_at = datetime.now()
        db.commit()
        logger.info(f"数据采集完成: {year}-{month}, 入库 {total_count} 条")
    except Exception as e:
        log.status = "failed"
        log.error_message = str(e)
        log.finished_at = datetime.now()
        db.commit()
        logger.error(f"数据采集失败: {year}-{month}: {e}")
        raise

    return {"year": year, "month": month, "records_count": total_count, "status": "success"}


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