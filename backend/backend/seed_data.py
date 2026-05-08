from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.overall import MonthlyOverall
from backend.models.brand import MonthlyBrand
from backend.models.model import MonthlyModel
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

# 清空旧数据
db.query(MonthlyOverall).delete()
db.query(MonthlyBrand).delete()
db.query(MonthlyModel).delete()
db.commit()

client = CpcaClient()

print("正在获取真实数据...")

# 1. 总体销量
overall_records = client.get_monthly_overall()
print(f"月度整体数据: {len(overall_records)} 条")

# 2. 新能源销量
nev_records = client.get_nev_overall()
print(f"新能源数据: {len(nev_records)} 条")

# 3. 品牌排名
brand_records = client.get_brand_ranking()
print(f"品牌数据: {len(brand_records)} 条")

# 4. 级别细分
segment_records = client.get_segment_data()
print(f"级别细分数据: {len(segment_records)} 条")

# 5. 国别数据
country_records = client.get_country_data()
print(f"国别数据: {len(country_records)} 条")

print("\n正在写入数据库...")

# 构建 nev 字典
nev_dict = {}
for r in nev_records:
    nev_dict[(r['year'], r['month'])] = r['新能源销量']

# 写入月度整体数据
for rec in overall_records:
    key = (rec['year'], rec['month'])
    total = rec['总销量']
    nev = nev_dict.get(key, 0)
    ice = total - nev if total > nev else 0
    penetration = round(nev / total * 100, 2) if total > 0 else 0

    row = MonthlyOverall(
        year=rec['year'],
        month=rec['month'],
        total_sales=total,
        nev_sales=nev,
        ice_sales=ice,
        bev_sales=nev * 0.7,
        phev_sales=nev * 0.25,
        hybrid_sales=nev * 0.05,
        nev_penetration_rate=penetration,
        data_type="retail",
        source="cpca"
    )
    db.add(row)

# 写入品牌数据
rank_by_month = {}
for rec in brand_records:
    key = (rec['year'], rec['month'])
    if key not in rank_by_month:
        rank_by_month[key] = []
    rank_by_month[key].append(rec)

# 新能源品牌列表
nev_brands = ['比亚迪汽车', '特斯拉中国', '蔚来', '小鹏汽车', '理想汽车', '广汽埃安', '零跑汽车', '哪吒汽车', '极氪', '深蓝汽车']

for (year, month), records in rank_by_month.items():
    sorted_records = sorted(records, key=lambda x: x['销量'], reverse=True)
    for rank, rec in enumerate(sorted_records, 1):
        brand_name = rec['品牌名称']
        is_nev = 1 if any(nev in brand_name for nev in nev_brands) else 0

        row = MonthlyBrand(
            year=year,
            month=month,
            brand_name=brand_name,
            sales_volume=rec['销量'],
            rank=rank,
            yoy_growth=0,
            mom_growth=0,
            is_nev=is_nev,
            data_type="retail",
            origin=_get_origin(brand_name),
            source="cpca"
        )
        db.add(row)

# 写入级别细分数据到 monthly_model 表
for rec in segment_records:
    row = MonthlyModel(
        year=rec['year'],
        month=rec['month'],
        model_name=f"轿车-{rec['级别']}",
        sales_volume=rec['销量'],
        segment=rec['级别'],
        energy_type="all",
        source="cpca"
    )
    db.add(row)

# 写入国别数据到 monthly_model 表
for rec in country_records:
    row = MonthlyModel(
        year=rec['year'],
        month=rec['month'],
        model_name=f"国别-{rec['国别']}",
        sales_volume=rec['销量'],
        segment="all",
        energy_type=rec['国别'],
        source="cpca"
    )
    db.add(row)

db.commit()
print("\n数据导入完成!")
print(f"月度整体数据: {db.query(MonthlyOverall).count()} 条")
print(f"品牌数据: {db.query(MonthlyBrand).count()} 条")
print(f"车型/细分数据: {db.query(MonthlyModel).count()} 条")
