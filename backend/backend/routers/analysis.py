from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from backend.core.database import get_db
from backend.models.overall import MonthlyOverall
from backend.models.brand import MonthlyBrand
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
            MonthlyOverall.year,
            func.sum(MonthlyOverall.total_sales).label("total_sales"),
            func.sum(MonthlyOverall.nev_sales).label("nev_sales"),
        ).filter(
            MonthlyOverall.year >= start_year,
            MonthlyOverall.data_type == "retail",
        ).group_by(MonthlyOverall.year).order_by(MonthlyOverall.year).all()

        data = []
        for r in yearly_rows:
            total = float(r.total_sales or 0)
            nev = float(r.nev_sales or 0)
            rate = (nev / total * 100) if total else 0
            data.append({"year": r.year, "nev_penetration_rate": round(rate, 2), "total_sales": total, "nev_sales": nev})
    else:
        rows = db.query(MonthlyOverall).filter(
            MonthlyOverall.year >= start_year,
            MonthlyOverall.data_type == "retail",
        ).order_by(MonthlyOverall.year, MonthlyOverall.month).all()

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
    row = db.query(MonthlyOverall).filter(
        MonthlyOverall.year == year,
        MonthlyOverall.month == month,
        MonthlyOverall.data_type == "retail",
    ).first()
    if not row:
        return success(None)

    total = float(row.total_sales) if row.total_sales else 0
    data = {
        "year": year,
        "month": month,
        "total_sales": total,
        "nev_sales": float(row.nev_sales) if row.nev_sales else 0,
        "nev_penetration_rate": float(row.nev_penetration_rate) if row.nev_penetration_rate else 0,
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
            MonthlyOverall.year,
            func.sum(MonthlyOverall.nev_sales).label("nev_sales"),
            func.sum(MonthlyOverall.bev_sales).label("bev_sales"),
            func.sum(MonthlyOverall.phev_sales).label("phev_sales"),
            func.sum(MonthlyOverall.hybrid_sales).label("hybrid_sales"),
        ).filter(
            MonthlyOverall.year >= start_year,
            MonthlyOverall.data_type == "retail",
        ).group_by(MonthlyOverall.year).order_by(MonthlyOverall.year).all()

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
        rows = db.query(MonthlyOverall).filter(
            MonthlyOverall.year >= start_year,
            MonthlyOverall.data_type == "retail",
        ).order_by(MonthlyOverall.year, MonthlyOverall.month).all()

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
    row = db.query(MonthlyOverall).filter(
        MonthlyOverall.year == year,
        MonthlyOverall.month == month,
        MonthlyOverall.data_type == "retail",
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
            MonthlyBrand.year,
            MonthlyBrand.brand_name,
            MonthlyBrand.origin,
            func.sum(MonthlyBrand.sales_volume).label("sales_volume"),
        ).filter(
            MonthlyBrand.year >= start_year,
            MonthlyBrand.source == "cpca",
            MonthlyBrand.data_type == "retail",
        ).group_by(MonthlyBrand.year, MonthlyBrand.brand_name, MonthlyBrand.origin).all()

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
        rows = db.query(MonthlyBrand).filter(
            MonthlyBrand.year >= start_year,
            MonthlyBrand.source == "cpca",
            MonthlyBrand.data_type == "retail",
        ).order_by(MonthlyBrand.year, MonthlyBrand.month).all()

        month_groups = {}
        for r in rows:
            key = (r.year, r.month)
            if key not in month_groups:
                month_groups[key] = []
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
    rows = db.query(MonthlyBrand).filter(
        MonthlyBrand.year == year,
        MonthlyBrand.month == month,
        MonthlyBrand.source == "cpca",
        MonthlyBrand.data_type == "retail",
    ).all()

    if not rows:
        return success(None)

    shares = _compute_origin_shares(rows)
    shares["year"] = year
    shares["month"] = month
    return success(shares)
