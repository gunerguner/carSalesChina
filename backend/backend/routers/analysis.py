from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from backend.core.database import get_db
from backend.models.overall import SalesData
from backend.models.brand import BrandSales, BrandMeta
from backend.schemas.response import success

router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])

ORIGIN_MAP = {
    "自主": ["比亚迪", "吉利汽车", "长安汽车", "长城汽车", "奇瑞", "蔚来", "小鹏", "理想", "零跑", "哪吒", "问界", "埃安", "红旗", "五菱", "荣威", "名爵", "传祺", "奔腾", "江淮", "北汽", "极氪", "深蓝", "智己", "岚图", "阿维塔", "领克", "魏牌", "坦克", "星途", "捷途", "宝骏", "东风", "海马", "东南", "大通", "北京", "东风风神", "东风风光", "极狐", "小米"],
    "德系": ["大众", "奥迪", "奔驰", "宝马", "保时捷", "斯柯达", "迈巴赫"],
    "日系": ["丰田", "本田", "日产", "马自达", "雷克萨斯", "英菲尼迪", "讴歌", "斯巴鲁", "三菱", "铃木"],
    "美系": ["别克", "雪佛兰", "凯迪拉克", "福特", "林肯", "Jeep", "特斯拉"],
    "欧系": ["沃尔沃", "标致", "雪铁龙", "DS", "捷豹", "路虎", "MINI", "Smart", "极星", "法拉利", "玛莎拉蒂", "兰博基尼", "宾利", "劳斯莱斯", "阿尔法·罗密欧"],
    "韩系": ["现代", "起亚", "捷尼赛思"],
}


def _get_origin(brand_name: str) -> str:
    for origin, brands in ORIGIN_MAP.items():
        for b in brands:
            if b in brand_name:
                return origin
    return "其他"


def _compute_origin_shares(rows):
    origin_totals = {}
    total_sales = 0
    for r in rows:
        origin = r.origin if r.origin else _get_origin(r.brand_name)
        sales = float(r.sales_volume or 0)
        if origin not in origin_totals:
            origin_totals[origin] = 0
        origin_totals[origin] += sales
        total_sales += sales

    result = {}
    if total_sales:
        for key in ["自主", "德系", "日系", "美系", "欧系", "韩系", "其他"]:
            val = origin_totals.get(key, 0)
            result[key] = round(val / total_sales * 100, 2)
    else:
        for key in ["自主", "德系", "日系", "美系", "欧系", "韩系", "其他"]:
            result[key] = 0

    return {
        "domestic": result.get("自主", 0),
        "german": result.get("德系", 0),
        "japanese": result.get("日系", 0),
        "american": result.get("美系", 0),
        "european": result.get("欧系", 0),
        "korean": result.get("韩系", 0),
        "other": result.get("其他", 0),
    }


@router.get("/nev-share/trend")
def nev_share_trend(
    years: int = Query(3),
    granularity: str = Query("monthly"),
    db: Session = Depends(get_db),
):
    now = datetime.now()
    start_year = now.year - years + 1

    if granularity == "yearly":
        yearly_rows = db.query(
            SalesData.year,
            func.sum(SalesData.total_sales).label("total_sales"),
            func.sum(SalesData.nev_sales).label("nev_sales"),
        ).filter(
            SalesData.year >= start_year,
            SalesData.data_type == "retail",
        ).group_by(SalesData.year).order_by(SalesData.year).all()

        data = []
        for r in yearly_rows:
            total = float(r.total_sales or 0)
            nev = float(r.nev_sales or 0)
            rate = (nev / total * 100) if total else 0
            data.append({"year": r.year, "nev_penetration_rate": round(rate, 2), "total_sales": total, "nev_sales": nev})
    else:
        rows = db.query(SalesData).filter(
            SalesData.year >= start_year,
            SalesData.data_type == "retail",
        ).order_by(SalesData.year, SalesData.month).all()

        data = []
        for r in rows:
            total = float(r.total_sales or 0)
            nev = float(r.nev_sales or 0)
            rate = (nev / total * 100) if total else 0
            data.append({
                "year": r.year, "month": r.month,
                "nev_penetration_rate": round(rate, 2),
                "total_sales": total, "nev_sales": nev,
            })

    return success(data)


@router.get("/nev-share/overview")
def nev_share_overview(
    year: int = Query(...),
    month: int = Query(...),
    db: Session = Depends(get_db),
):
    row = db.query(SalesData).filter(
        SalesData.year == year,
        SalesData.month == month,
        SalesData.data_type == "retail",
    ).first()
    if not row:
        return success(None)

    total = float(row.total_sales) if row.total_sales else 0
    nev = float(row.nev_sales) if row.nev_sales else 0
    nev_penetration_rate = (nev / total * 100) if total else 0

    data = {
        "year": year,
        "month": month,
        "total_sales": total,
        "nev_sales": nev,
        "nev_penetration_rate": round(nev_penetration_rate, 2),
        "breakdown": [
            {"name": "纯电动", "value": float(row.bev_sales) if row.bev_sales else 0},
            {"name": "插电混动", "value": float(row.phev_sales) if row.phev_sales else 0},
            {"name": "其他混动", "value": float(row.hybrid_sales) if row.hybrid_sales else 0},
            {"name": "燃油车", "value": float(row.ice_sales) if row.ice_sales else 0},
        ],
    }

    return success(data)


@router.get("/nev-breakdown")
def nev_breakdown(
    years: int = Query(3),
    granularity: str = Query("monthly"),
    db: Session = Depends(get_db),
):
    now = datetime.now()
    start_year = now.year - years + 1

    if granularity == "yearly":
        yearly_rows = db.query(
            SalesData.year,
            func.sum(SalesData.nev_sales).label("nev_sales"),
            func.sum(SalesData.bev_sales).label("bev_sales"),
            func.sum(SalesData.phev_sales).label("phev_sales"),
            func.sum(SalesData.hybrid_sales).label("hybrid_sales"),
        ).filter(
            SalesData.year >= start_year,
            SalesData.data_type == "retail",
        ).group_by(SalesData.year).order_by(SalesData.year).all()

        data = []
        for r in yearly_rows:
            nev = float(r.nev_sales or 0)
            bev = float(r.bev_sales or 0)
            phev = float(r.phev_sales or 0)
            hybrid = float(r.hybrid_sales or 0)
            data.append({
                "year": r.year,
                "nev_sales": nev,
                "bev_sales": bev, "bev_ratio": round(bev / nev * 100, 2) if nev else 0,
                "phev_sales": phev, "phev_ratio": round(phev / nev * 100, 2) if nev else 0,
                "hybrid_sales": hybrid, "hybrid_ratio": round(hybrid / nev * 100, 2) if nev else 0,
            })
    else:
        rows = db.query(SalesData).filter(
            SalesData.year >= start_year,
            SalesData.data_type == "retail",
        ).order_by(SalesData.year, SalesData.month).all()

        data = []
        for r in rows:
            nev = float(r.nev_sales or 0)
            bev = float(r.bev_sales or 0)
            phev = float(r.phev_sales or 0)
            hybrid = float(r.hybrid_sales or 0)
            data.append({
                "year": r.year, "month": r.month,
                "nev_sales": nev,
                "bev_sales": bev, "bev_ratio": round(bev / nev * 100, 2) if nev else 0,
                "phev_sales": phev, "phev_ratio": round(phev / nev * 100, 2) if nev else 0,
                "hybrid_sales": hybrid, "hybrid_ratio": round(hybrid / nev * 100, 2) if nev else 0,
            })

    return success(data)


@router.get("/nev-breakdown/detail")
def nev_breakdown_detail(
    year: int = Query(...),
    month: int = Query(...),
    db: Session = Depends(get_db),
):
    row = db.query(SalesData).filter(
        SalesData.year == year,
        SalesData.month == month,
        SalesData.data_type == "retail",
    ).first()
    if not row:
        return success(None)

    nev = float(row.nev_sales) if row.nev_sales else 0
    bev = float(row.bev_sales) if row.bev_sales else 0
    phev = float(row.phev_sales) if row.phev_sales else 0
    hybrid = float(row.hybrid_sales) if row.hybrid_sales else 0

    return success({
        "year": year, "month": month,
        "nev_sales": nev,
        "bev_sales": bev, "bev_ratio": round(bev / nev * 100, 2) if nev else 0,
        "phev_sales": phev, "phev_ratio": round(phev / nev * 100, 2) if nev else 0,
        "hybrid_sales": hybrid, "hybrid_ratio": round(hybrid / nev * 100, 2) if nev else 0,
        "ice_sales": float(row.ice_sales) if row.ice_sales else 0,
    })


@router.get("/origin-share/trend")
def origin_share_trend(
    years: int = Query(3),
    granularity: str = Query("monthly"),
    db: Session = Depends(get_db),
):
    now = datetime.now()
    start_year = now.year - years + 1

    if granularity == "yearly":
        rows = db.query(
            BrandSales.year,
            BrandSales.brand_name,
            BrandMeta.origin,
            func.sum(BrandSales.sales_volume).label("sales_volume"),
        ).outerjoin(
            BrandMeta, BrandMeta.brand_name == BrandSales.brand_name
        ).filter(
            BrandSales.year >= start_year,
            BrandSales.data_type == "retail",
        ).group_by(BrandSales.year, BrandSales.brand_name, BrandMeta.origin).all()

        year_groups = {}
        for r in rows:
            if r.year not in year_groups:
                year_groups[r.year] = []
            year_groups[r.year].append(r)

        data = []
        for year in sorted(year_groups.keys()):
            shares = _compute_origin_shares(year_groups[year])
            shares["year"] = year
            data.append(shares)
    else:
        rows = db.query(BrandSales).filter(
            BrandSales.year >= start_year,
            BrandSales.data_type == "retail",
        ).order_by(BrandSales.year, BrandSales.month).all()

        brand_names = [r.brand_name for r in rows]
        metas = db.query(BrandMeta).filter(BrandMeta.brand_name.in_(brand_names)).all()
        meta_map = {m.brand_name: m for m in metas}

        month_groups = {}
        for r in rows:
            key = (r.year, r.month)
            if key not in month_groups:
                month_groups[key] = []
            r.origin = meta_map.get(r.brand_name).origin if meta_map.get(r.brand_name) else None
            month_groups[key].append(r)

        data = []
        for (year, month) in sorted(month_groups.keys()):
            shares = _compute_origin_shares(month_groups[(year, month)])
            shares["year"] = year
            shares["month"] = month
            data.append(shares)

    return success(data)


@router.get("/origin-share/overview")
def origin_share_overview(
    year: int = Query(...),
    month: int = Query(...),
    db: Session = Depends(get_db),
):
    rows = db.query(BrandSales).filter(
        BrandSales.year == year,
        BrandSales.month == month,
        BrandSales.data_type == "retail",
    ).all()

    if not rows:
        return success(None)

    brand_names = [r.brand_name for r in rows]
    metas = db.query(BrandMeta).filter(BrandMeta.brand_name.in_(brand_names)).all()
    meta_map = {m.brand_name: m for m in metas}

    for r in rows:
        r.origin = meta_map.get(r.brand_name).origin if meta_map.get(r.brand_name) else None

    shares = _compute_origin_shares(rows)
    shares["year"] = year
    shares["month"] = month
    return success(shares)