from sqlmodel import Session, select

from backend.core.exceptions import NotFoundAppError, ValidationAppError
from backend.models.brand import BrandMeta, BrandSales


def get_all_brand_meta(db: Session) -> list[dict]:
    rows = db.exec(select(BrandMeta).order_by(BrandMeta.brand_name.asc())).all()
    return [
        {
            "brand_id": row.id,
            "brand_name": row.brand_name,
        }
        for row in rows
        if row.brand_name
    ]


def get_brand_trend_all_periods(
    db: Session,
    brand_names: list[str],
    data_type: str,
) -> list[dict]:
    names = [name.strip() for name in brand_names if name.strip()][:3]
    if not names:
        raise ValidationAppError("brand_names 不能为空")

    if data_type not in {"retail", "production"}:
        raise ValidationAppError("data_type 仅支持 retail 或 production")

    metas = db.exec(select(BrandMeta).where(BrandMeta.brand_name.in_(names))).all()
    found_names = {meta.brand_name for meta in metas if meta.brand_name}
    missing = [name for name in names if name not in found_names]
    if missing:
        raise NotFoundAppError(f"品牌不存在: {', '.join(missing)}")

    id_to_name = {meta.id: meta.brand_name for meta in metas}
    ids = list(id_to_name.keys())

    rows = db.exec(
        select(BrandSales).where(
            BrandSales.brand_id.in_(ids),
            BrandSales.data_type == data_type,
            BrandSales.level_type == "all",
            BrandSales.date_type == "monthly",
        ).order_by(BrandSales.year, BrandSales.month)
    ).all()

    data = {name: {"brand_name": name, "monthly_data": []} for name in names}
    for row in rows:
        brand_name = id_to_name.get(row.brand_id)
        if brand_name is None:
            continue
        data.setdefault(brand_name, {"brand_name": brand_name, "monthly_data": []})
        data[brand_name]["monthly_data"].append(
            {
                "year": row.year,
                "month": row.month,
                "sales": float(row.sales_volume or 0),
            }
        )

    return [data[name] for name in names]
