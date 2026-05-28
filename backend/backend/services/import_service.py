import logging
from importlib.resources import files
from typing import Any, cast

import yaml
from sqlalchemy import text
from sqlmodel import Session, select

from backend.common.types import BrandSalesRecord, BrandSalesUpsertRow
from backend.core.exceptions import AppError, ExternalSourceAppError
from backend.models.brand import BrandMeta, BrandSales
from backend.models.origin import OriginShareData
from backend.models.overall import SalesData
from backend.sources.cpca_client import CpcaClient
from backend.sources.yiche_client import YicheBrandClient, YicheOverallClient

logger = logging.getLogger(__name__)

cpca_client = CpcaClient()
yiche_overall_client = YicheOverallClient()
yiche_brand_client = YicheBrandClient()


def _batch_upsert(
    db: Session,
    model: type,
    records: list[dict[str, Any]],
    fields: list[str],
    batch_size: int = 500,
) -> int:
    if not records:
        return 0

    table = model.__tablename__
    cols = ", ".join(fields)
    updates = ", ".join(f"{field}=VALUES({field})" for field in fields)
    placeholders = ", ".join(f":{field}" for field in fields)
    sql = text(
        f"INSERT INTO {table} ({cols}) VALUES ({placeholders}) "
        f"ON DUPLICATE KEY UPDATE {updates}"
    )

    total = 0
    for i in range(0, len(records), batch_size):
        batch = records[i : i + batch_size]
        db.execute(sql, [{field: rec.get(field) for field in fields} for rec in batch])
        db.commit()
        total += len(batch)
    return total


def _refresh_status(overall_ok: bool, brand_ok: bool) -> str:
    match (overall_ok, brand_ok):
        case (True, True):
            return "success"
        case (False, False):
            return "failed"
        case _:
            return "partial_failure"


def _normalize_brand_records(
    records: list[BrandSalesRecord],
    master_id_to_brand_id: dict[int, int],
) -> list[BrandSalesUpsertRow]:
    return [
        {
            "year": rec["year"],
            "month": rec["month"],
            "brand_id": brand_id,
            "sales_volume": rec.get("sales_volume"),
            "data_type": rec.get("data_type", "retail"),
            "date_type": rec.get("date_type", "monthly"),
            "level_type": rec.get("level_type", "all"),
        }
        for rec in records
        if (brand_id := master_id_to_brand_id.get(rec["master_id"]))
    ]


META_DATA_PATH = files("backend") / "meta_data.yaml"


def refresh_brand_meta(db: Session) -> dict:
    try:
        if not META_DATA_PATH.exists():
            raise AppError(message=f"meta_data.yaml 不存在: {META_DATA_PATH}")

        with open(META_DATA_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise AppError(message="meta_data.yaml 格式错误，根节点必须是对象")

        brands: dict = data.get("brands", {})
        if not brands:
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
                db.add(
                    BrandMeta(
                        brand_name=cn_name, brand_name_en=en_name, master_id=master_id
                    )
                )
                inserted += 1

        db.commit()
        logger.info("BrandMeta 刷新完成: 新增 %s, 更新 %s", inserted, updated)
        return {
            "inserted": inserted,
            "updated": updated,
            "total": len(brands),
            "status": "success",
        }
    except Exception:
        logger.exception("BrandMeta 刷新失败")
        raise


def refresh_sales_data(db: Session) -> dict:
    try:
        overall_fr = yiche_overall_client.fetch_overall_sales()
        overall_count = _batch_upsert(
            db,
            SalesData,
            overall_fr.records,
            ["year", "month", "sales", "data_type", "date_type", "level_type"],
        )

        rows = db.exec(select(BrandMeta).where(BrandMeta.master_id.isnot(None))).all()
        brand_count = 0
        brand_fr = None
        if rows:
            master_id_to_brand_id = {r.master_id: r.id for r in rows}
            master_ids = list(master_id_to_brand_id.keys())
            brand_fr = yiche_brand_client.fetch_brand_sales(master_ids)

            normalized = _normalize_brand_records(
                cast(list[BrandSalesRecord], brand_fr.records),
                master_id_to_brand_id,
            )

            brand_count = _batch_upsert(
                db,
                BrandSales,
                normalized,
                [
                    "year",
                    "month",
                    "brand_id",
                    "sales_volume",
                    "data_type",
                    "date_type",
                    "level_type",
                ],
            )

        total_count = overall_count + brand_count

        has_brand_job = bool(rows)
        overall_ok = overall_fr.ok
        brand_ok = True if not has_brand_job else (brand_fr is not None and brand_fr.ok)
        refresh_status = _refresh_status(overall_ok, brand_ok)

        source_errors: dict[str, str | None] = {
            "overall": overall_fr.error_summary(),
            "brand": brand_fr.error_summary() if brand_fr else None,
        }

        logger.info(
            "销量数据刷新完成: 总体 %s 条, 品牌 %s 条, status=%s",
            overall_count,
            brand_count,
            refresh_status,
        )
        if refresh_status == "failed":
            raise ExternalSourceAppError(
                f"外部源全部失败: overall={source_errors['overall']}; brand={source_errors['brand']}"
            )
        return {
            "overall_count": overall_count,
            "brand_count": brand_count,
            "records_count": total_count,
            "status": refresh_status,
            "source_errors": source_errors,
        }
    except Exception:
        logger.exception("销量数据刷新失败")
        raise


def refresh_origin_data(db: Session) -> dict:
    try:
        origin_fr = cpca_client.get_country_data()

        origin_count = _batch_upsert(
            db,
            OriginShareData,
            origin_fr.records,
            ["year", "month", "origin", "sales_volume"],
        )

        refresh_status = "success" if origin_fr.ok else "failed"
        logger.info(
            "国别数据刷新完成: %s 条, status=%s", origin_count, refresh_status
        )
        if refresh_status == "failed":
            raise ExternalSourceAppError(
                f"外部源失败: origin={origin_fr.error_summary()}"
            )
        return {
            "origin_count": origin_count,
            "records_count": origin_count,
            "status": refresh_status,
            "source_errors": {"origin": origin_fr.error_summary()},
        }
    except Exception:
        logger.exception("国别数据刷新失败")
        raise
