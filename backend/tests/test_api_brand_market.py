"""API 层：/api/v1/market 与 /api/v1/brands（信封 + 错误映射）。"""

from tests.conftest import add_brand_meta, add_brand_sales, add_sales


class TestMarketRaw:
    def test_envelope_and_rows(self, client, db_session):
        add_sales(db_session, year=2024, month=1, sales=100.0)
        db_session.commit()
        resp = client.get("/api/v1/market/raw")
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert body["message"] == "success"
        assert body["data"] == [
            {"year": 2024, "month": 1, "data_type": "retail", "level_type": "all", "sales": 100.0}
        ]

    def test_empty_data(self, client):
        resp = client.get("/api/v1/market/raw")
        assert resp.status_code == 200
        assert resp.json()["data"] == []


class TestBrandMetaAll:
    def test_envelope(self, client, db_session):
        add_brand_meta(db_session, brand_name="比亚迪", brand_name_en="byd", master_id=100)
        db_session.commit()
        resp = client.get("/api/v1/brands/meta/all")
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        meta = body["data"]
        assert len(meta) == 1
        assert meta[0]["brand_name"] == "比亚迪"
        assert isinstance(meta[0]["brand_id"], int)

    def test_empty_data(self, client):
        assert client.get("/api/v1/brands/meta/all").json()["data"] == []


class TestBrandTrendAllPeriods:
    @staticmethod
    def _seed(db_session):
        byd = add_brand_meta(db_session, brand_name="比亚迪", brand_name_en="byd", master_id=100)
        li = add_brand_meta(db_session, brand_name="理想", brand_name_en="li", master_id=101)
        add_brand_sales(db_session, brand_id=byd.id, year=2024, month=1, sales_volume=20.0)
        add_brand_sales(db_session, brand_id=li.id, year=2024, month=1, sales_volume=3.0)
        db_session.commit()

    def test_comma_separated_names(self, client, db_session):
        self._seed(db_session)
        resp = client.get(
            "/api/v1/brands/trend-all-periods", params={"brand_names": "比亚迪,理想"}
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert [s["brand_name"] for s in data] == ["比亚迪", "理想"]
        assert data[0]["monthly_data"] == [{"year": 2024, "month": 1, "sales": 20.0}]

    def test_repeated_query_params(self, client, db_session):
        self._seed(db_session)
        resp = client.get(
            "/api/v1/brands/trend-all-periods",
            params=[("brand_names", "比亚迪"), ("brand_names", "理想")],
        )
        assert resp.status_code == 200
        assert len(resp.json()["data"]) == 2

    def test_more_than_four_truncated(self, client, db_session):
        for i in range(6):
            meta = add_brand_meta(db_session, brand_name=f"品牌{i}", brand_name_en=f"b{i}", master_id=i)
            add_brand_sales(db_session, brand_id=meta.id, year=2024, month=1, sales_volume=1.0)
        db_session.commit()
        resp = client.get(
            "/api/v1/brands/trend-all-periods",
            params={"brand_names": "品牌0,品牌1,品牌2,品牌3,品牌4,品牌5"},
        )
        assert resp.status_code == 200
        assert len(resp.json()["data"]) == 4  # MAX_BRAND_COMPARE 截断

    def test_missing_brand_maps_to_404_envelope(self, client, db_session):
        self._seed(db_session)
        resp = client.get(
            "/api/v1/brands/trend-all-periods", params={"brand_names": "蔚来"}
        )
        assert resp.status_code == 404
        body = resp.json()
        assert body["code"] == 1003
        assert "蔚来" in body["message"]

    def test_empty_names_maps_to_422_envelope(self, client):
        resp = client.get("/api/v1/brands/trend-all-periods", params={"brand_names": " , "})
        assert resp.status_code == 422
        body = resp.json()
        assert body["code"] == 1001

    def test_missing_param_maps_to_422(self, client):
        resp = client.get("/api/v1/brands/trend-all-periods")
        assert resp.status_code == 422
        assert resp.json()["code"] == 1001

    def test_data_type_filter(self, client, db_session):
        byd = add_brand_meta(db_session, brand_name="比亚迪", brand_name_en="byd", master_id=100)
        add_brand_sales(db_session, brand_id=byd.id, year=2024, month=1, sales_volume=20.0)
        add_brand_sales(
            db_session, brand_id=byd.id, year=2024, month=2, sales_volume=99.0, data_type="production"
        )
        db_session.commit()
        resp = client.get(
            "/api/v1/brands/trend-all-periods",
            params={"brand_names": "比亚迪", "data_type": "production"},
        )
        data = resp.json()["data"]
        assert [p["month"] for p in data[0]["monthly_data"]] == [2]
