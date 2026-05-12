import logging
from datetime import datetime
from pathlib import Path
from typing import Iterable

import yaml
from sqlmodel import Session, select
from sqlalchemy import text

from backend.models.brand import BrandMeta, BrandSales
from backend.models.log import CollectionLog
from backend.models.origin import OriginShareData
from backend.models.overall import SalesData
from backend.sources.cpca_client import CpcaClient
from backend.sources.yiche_client import YicheClient

logger = logging.getLogger(__name__)

client = CpcaClient()
yiche_client = YicheClient()
DEFAULT_IMPORT_DATA_TYPES = ("retail", "wholesale", "production")
BRAND_DATA_TYPES = ("retail", "wholesale")


def _batch_upsert(db: Session, model: type, records: list[dict], fields: list[str]) -> int:
    if not records:
        return 0
    table = model.__tablename__
    cols = ", ".join(fields)
    updates = ", ".join([f"{f}=VALUES({f})" for f in fields])
    placeholders = "(" + ", ".join([f":{f}" for f in fields]) + ")"
    sql = f"INSERT INTO {table} ({cols}) VALUES "
    sql += ", ".join([placeholders] * len(records))
    sql += f" ON DUPLICATE KEY UPDATE {updates}"
    params_list = [{f: rec.get(f) for f in fields} for rec in records]
    db.execute(text(sql), params_list)
    db.commit()
    return len(records)


def upsert_brand_meta(db: Session, brands: dict) -> int:
    records = []
    for name, info in brands.items():
        rec = {"brand_name": name}
        if isinstance(info, dict):
            rec["brand_name_en"] = info.get("brand_name_en")
            rec["master_id"] = info.get("master_id")
        else:
            rec["brand_name_en"] = info
        records.append(rec)
    return _batch_upsert(db, BrandMeta, records, ["brand_name", "brand_name_en", "master_id"])


def _get_brand_id_map(db: Session, brand_names: Iterable[str]) -> dict[str, int]:
    names = sorted(set(brand_names))
    if not names:
        return {}
    existing = db.exec(select(BrandMeta).where(BrandMeta.brand_name.in_(names))).all()
    existing_names = {r.brand_name for r in existing}
    new_names = [n for n in names if n not in existing_names]
    for name in new_names:
        db.add(BrandMeta(brand_name=name))
    if new_names:
        db.commit()
    rows = db.exec(select(BrandMeta).where(BrandMeta.brand_name.in_(names))).all()
    return {r.brand_name: r.id for r in rows}


def _upsert_overall(db: Session, records: list[dict]) -> int:
    fields = ["year", "month", "sales", "data_type", "date_type", "level_type"]
    return _batch_upsert(db, SalesData, records, fields)


def _upsert_total_sales(db: Session, records: list[dict]) -> int:
    fields = ["year", "month", "sales", "data_type", "date_type", "level_type"]
    return _batch_upsert(db, SalesData, records, fields)


def refresh_total_sales_data(db: Session) -> dict:
    log = CollectionLog(
        task_type="refresh_total_sales",
        status="pending",
        started_at=datetime.now(),
    )
    db.add(log)
    db.commit()

    try:
        records = yiche_client.fetch_all()
        count = _upsert_total_sales(db, records)

        log.status = "success"
        log.records_count = count
        log.finished_at = datetime.now()
        db.commit()
        logger.info("总销量数据刷新完成: %s 条", count)
        return {
            "records_count": count,
            "status": "success",
        }
    except Exception as e:
        log.status = "failed"
        log.error_message = str(e)
        log.finished_at = datetime.now()
        db.commit()
        logger.error("总销量数据刷新失败: %s", e)
        raise


def _upsert_brand(db: Session, records: list[dict]) -> int:
    brand_names = [r.get("品牌名称", "") for r in records if r.get("品牌名称")]
    brand_id_map = _get_brand_id_map(db, brand_names)
    normalized = []
    for rec in records:
        brand_name = rec.get("品牌名称", "")
        if not brand_name:
            continue
        brand_id = brand_id_map.get(brand_name)
        if not brand_id:
            continue
        normalized.append({
            "year": rec["year"],
            "month": rec["month"],
            "brand_id": brand_id,
            "sales_volume": rec.get("销量"),
            "data_type": rec.get("data_type", "retail"),
        })
    return _batch_upsert(db, BrandSales, normalized, ["year", "month", "brand_id", "sales_volume", "data_type"])


def _upsert_origin_share(db: Session, records: list[dict]) -> int:
    fields = ["year", "month", "origin", "sales_volume", "data_type"]
    return _batch_upsert(db, OriginShareData, records, fields)


META_DATA_PATH = Path(__file__).resolve().parent.parent / "meta_data.yaml"


def refresh_brand_meta(db: Session) -> dict:
    if not META_DATA_PATH.exists():
        raise FileNotFoundError(f"meta_data.yaml 不存在: {META_DATA_PATH}")

    with open(META_DATA_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    brands: dict = data.get("brands", {})
    if not brands:
        logger.warning("meta_data.yaml 中没有 brands 数据")
        return {"status": "skipped", "reason": "no brands in yaml"}

    existing_rows = db.exec(select(BrandMeta)).all()
    existing_map = {r.brand_name: r for r in existing_rows}

    updated = 0
    inserted = 0
    for en_name, info in brands.items():
        cn_name = info.get("name", "") if isinstance(info, dict) else str(info)
        master_id = info.get("master_id") if isinstance(info, dict) else None
        if not cn_name:
            continue
        if cn_name in existing_map:
            row = existing_map[cn_name]
            changed = False
            if en_name and row.brand_name_en != en_name:
                row.brand_name_en = en_name
                changed = True
            if master_id is not None and row.master_id != master_id:
                row.master_id = master_id
                changed = True
            if changed:
                updated += 1
        else:
            db.add(BrandMeta(brand_name=cn_name, brand_name_en=en_name, master_id=master_id))
            inserted += 1

    db.commit()
    logger.info("BrandMeta 刷新完成: 新增 %s, 更新 %s", inserted, updated)
    return {"inserted": inserted, "updated": updated, "total": len(brands), "status": "success"}


def refresh_all_sales_data(
    db: Session,
    data_types: Iterable[str] = DEFAULT_IMPORT_DATA_TYPES,
) -> dict:
    data_types = tuple(data_types)
    log = CollectionLog(
        task_type="refresh_all_sales",
        status="pending",
        started_at=datetime.now(),
    )
    db.add(log)
    db.commit()

    try:
        brand_records = []
        for data_type in data_types:
            if data_type in BRAND_DATA_TYPES:
                brand_records.extend(client.get_brand_ranking(data_type=data_type))

        brand_count = _upsert_brand(db, brand_records)
        origin_records = client.get_country_data()
        origin_count = _upsert_origin_share(db, origin_records)

        total_count = brand_count + origin_count

        log.status = "success"
        log.records_count = total_count
        log.finished_at = datetime.now()
        db.commit()
        logger.info(
            "全量数据刷新完成: 品牌 %s 条, 国别 %s 条",
            brand_count,
            origin_count,
        )
        return {
            "data_types": list(data_types),
            "brand_count": brand_count,
            "origin_count": origin_count,
            "records_count": total_count,
            "status": "success",
        }
    except Exception as e:
        log.status = "failed"
        log.error_message = str(e)
        log.finished_at = datetime.now()
        db.commit()
        logger.error("全量数据刷新失败: %s", e)
        raise
