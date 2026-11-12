"""API 层：/api/v1/analysis 三个读接口（信封 + 参数校验 + 业务规则）。"""


class TestNevShareTrend:
    def test_envelope_and_values(self, client, analysis_dataset):
        resp = client.get("/api/v1/analysis/nev-share/trend", params={"years": 2})
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert [r["nev_penetration_rate"] for r in body["data"]] == [30.0, 40.0, 40.0]

    def test_yearly_granularity(self, client, analysis_dataset):
        resp = client.get(
            "/api/v1/analysis/nev-share/trend",
            params={"years": 2, "granularity": "yearly"},
        )
        data = resp.json()["data"]
        assert len(data) == 2
        assert data[0]["nev_penetration_rate"] == 36.67

    @staticmethod
    def _assert_422(resp):
        assert resp.status_code == 422
        body = resp.json()
        assert body["code"] == 1001
        assert body["data"] is None

    def test_invalid_years(self, client):
        self._assert_422(client.get("/api/v1/analysis/nev-share/trend", params={"years": 0}))
        self._assert_422(client.get("/api/v1/analysis/nev-share/trend", params={"years": 11}))

    def test_invalid_granularity(self, client):
        self._assert_422(
            client.get("/api/v1/analysis/nev-share/trend", params={"granularity": "quarterly"})
        )

    def test_defaults_years3_monthly(self, client, analysis_dataset):
        resp = client.get("/api/v1/analysis/nev-share/trend")
        assert resp.status_code == 200
        assert len(resp.json()["data"]) == 3  # 默认 years=3 覆盖数据集全部


class TestNevBreakdown:
    def test_phev_is_nev_minus_bev(self, client, analysis_dataset):
        resp = client.get("/api/v1/analysis/nev-breakdown", params={"years": 2})
        first = resp.json()["data"][0]
        assert (first["nev_sales"], first["bev_sales"], first["phev_sales"]) == (30.0, 10.0, 20.0)
        assert (first["bev_ratio"], first["phev_ratio"]) == (33.33, 66.67)

    def test_empty_db_returns_empty_list(self, client):
        assert client.get("/api/v1/analysis/nev-breakdown").json()["data"] == []


class TestOriginShareTrend:
    def test_envelope_and_mapping(self, client, origin_dataset):
        resp = client.get("/api/v1/analysis/origin-share/trend", params={"years": 2})
        assert resp.status_code == 200
        data = resp.json()["data"]
        first = data[0]
        assert (first["domestic"], first["german"], first["japanese"]) == (60.0, 25.0, 15.0)

    def test_empty_db_returns_empty_list(self, client):
        assert client.get("/api/v1/analysis/origin-share/trend").json()["data"] == []
