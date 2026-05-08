from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.overall import SalesData
from backend.models.brand import BrandSales, BrandMeta
from backend.sources.cpca_client import CpcaClient

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

DATABASE_URL = "mysql+pymysql://root:root@localhost/car_sales"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

db.query(BrandSales).delete()
db.query(SalesData).delete()
db.query(BrandMeta).delete()
db.commit()

client = CpcaClient()

print("正在获取真实数据...")

overall_records = client.get_monthly_overall()
print(f"月度整体数据: {len(overall_records)} 条")

nev_records = client.get_nev_overall()
print(f"新能源数据: {len(nev_records)} 条")

brand_records = client.get_brand_ranking()
print(f"品牌数据: {len(brand_records)} 条")

print("\n正在写入数据库...")

nev_dict = {}
for r in nev_records:
    nev_dict[(r['year'], r['month'])] = r['新能源销量']

for rec in overall_records:
    key = (rec['year'], rec['month'])
    total = rec['总销量']
    nev = nev_dict.get(key, 0)
    ice = total - nev if total > nev else 0

    row = SalesData(
        year=rec['year'],
        month=rec['month'],
        total_sales=total,
        nev_sales=nev,
        ice_sales=ice,
        bev_sales=nev * 0.7,
        phev_sales=nev * 0.25,
        hybrid_sales=nev * 0.05,
        data_type="retail",
    )
    db.add(row)

rank_by_month = {}
for rec in brand_records:
    key = (rec['year'], rec['month'])
    if key not in rank_by_month:
        rank_by_month[key] = []
    rank_by_month[key].append(rec)

brand_meta_set = set()

for (year, month), records in rank_by_month.items():
    for rec in records:
        brand_name = rec['品牌名称']
        origin = _get_origin(brand_name)

        if brand_name not in brand_meta_set:
            meta = BrandMeta(
                brand_name=brand_name,
                origin=origin,
            )
            db.add(meta)
            brand_meta_set.add(brand_name)

        row = BrandSales(
            year=year,
            month=month,
            brand_name=brand_name,
            sales_volume=rec['销量'],
            yoy_growth=0,
            mom_growth=0,
            data_type="retail",
        )
        db.add(row)

db.commit()
print("\n数据导入完成!")
print(f"销售数据: {db.query(SalesData).count()} 条")
print(f"品牌元数据: {db.query(BrandMeta).count()} 条")
print(f"品牌销量: {db.query(BrandSales).count()} 条")