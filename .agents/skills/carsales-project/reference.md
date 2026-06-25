# carSales 详细参考

SKILL.md 的扩展材料；改表结构、外部源、部署时按需阅读。

## 关键文件索引

| 用途 | 路径 |
|------|------|
| FastAPI 入口 | `backend/backend/main.py` |
| 配置 | `backend/backend/config.py` |
| 数据库会话 | `backend/backend/core/database.py` |
| CSRF | `backend/backend/core/csrf.py` |
| 异常处理 | `backend/backend/core/exception_handlers.py`（全局映射） |
| 业务异常类 | `backend/backend/core/exceptions.py`（`AppError`、`ExternalSourceAppError` 等） |
| 错误码 | `backend/backend/core/error_codes.py` |
| 管理装饰器 | `backend/backend/core/decorators.py`（`@handle_try_catch_action`、`@handle_success_response`） |
| 公共工具 | `backend/backend/common/`（见下节） |
| 分析查询 schema | `backend/backend/schemas/analysis.py`（`AnalysisTrendQuery`：`years`、`granularity`） |
| 模型 | `backend/backend/models/`（`overall.py`、`brand.py`、`origin.py`） |
| 路由 | `backend/backend/routers/` |
| 采集编排 | `backend/backend/services/import_service.py` |
| 市场/品牌/分析 | `market_service.py`、`brand_service.py`、`analysis_service.py` |
| 易车客户端 | `backend/backend/sources/yiche_client.py` |
| 乘联会客户端 | `backend/backend/sources/cpca_client.py` |
| 拉取结果类型 | `backend/backend/sources/fetch_result.py`（见下节） |
| 品牌 YAML | `backend/backend/meta_data.yaml` |
| 国别字段映射 | `backend/backend/origin_field_map.yaml` |
| 建表脚本 | `backend/init_db.sql` |
| Vite/代理 | `frontend/apps/web-tdesign/vite.config.mts` |
| 请求客户端 | `frontend/apps/web-tdesign/src/api/request.ts` |
| 读 API | `frontend/apps/web-tdesign/src/api/`（`market.ts`、`brand.ts`、`analysis.ts`） |
| 管理刷新 API | `frontend/apps/web-tdesign/src/api/admin.ts` |
| 路由模块 | `frontend/apps/web-tdesign/src/router/routes/modules/app.ts` |
| 市场页 | `frontend/apps/web-tdesign/src/views/market/` |
| 品牌页 | `frontend/apps/web-tdesign/src/views/brand/` |
| 分析页（NEV） | `frontend/apps/web-tdesign/src/views/nev/` |
| 分析页（车系占比） | `frontend/apps/web-tdesign/src/views/origin/` |
| Docker Compose | `docker/docker-compose.yml` |
| Nginx | `docker/nginx.conf` |
| 环境模板 | `backend/.env.example`、`docker/.env.example` |

## 公共类型与周期聚合（`common/`）

**`types.py`**：`DataType`、`DateType`、`LevelType`、`Granularity` 等 `Literal`；以及 API/入库行 `TypedDict`：

| TypedDict | 用途 |
|-----------|------|
| `MarketRawRow`、`OverallSalesRecord`、`BrandSalesRecord` | 市场/易车采集行 |
| `BrandSalesUpsertRow`、`OriginShareUpsertRow` | 入库 upsert 行 |
| `AnalysisPeriodRow` | 分析周期基类（`year`、可选 `month`） |
| `NevShareTrendRow`、`NevBreakdownRow`、`OriginShareTrendRow` | 分析 API 响应行 |

**`periods.py`**：分析读路径共用周期键与 SQL 分组列：

- `PeriodKey(year, month?)`：年度粒度时 `month=None`
- `period_columns(model_cls, granularity)` → `(year,)` 或 `(year, month)`
- `period_key(row, granularity)`、`period_entry(key)` → `AnalysisPeriodRow`
- `LevelSalesByPeriod`：`dict[PeriodKey, dict[LevelType, float]]`

`analysis_service.py` 对 `SalesData` / `OriginShareData` 按上述工具做 `years` 窗口 + 月度/年度聚合；国别份额百分比字段名来自 `origin_field_map.yaml`（中文列名 → 英文键）。

## 外部源拉取结果层次（`fetch_result.py`）

| 类型 | 层级 | 说明 |
|------|------|------|
| `HttpJsonResult` | HTTP | `body` / `error`；易车 `_safe_get_json` |
| `SliceResult[T]` | 单次切片 | 单维度或单次 AkShare 拉取 |
| `KeyedSliceResult[T]` | 并发切片 | 带 `key` 的品牌并发批次 |
| `SourceFetchResult` | 对外 | `import_service` 消费的统一结果；含 `error_summary()` |

易车：`YicheOverallClient` 按 `OverallFetchDim` 切片；`YicheBrandClient` 按 `BrandFetchDim` + `master_id` 批次并发，归一化为 `OverallSalesRecord` / `BrandSalesRecord`。乘联会：`CpcaClient.get_country_data()` 内部 `SliceResult` → `SourceFetchResult`，记录为 `OriginShareUpsertRow`。

## 数据库表

| 表 | 用途 | 唯一键要点 |
|----|------|------------|
| `sales_data` | 总体销量（易车） | year, month, data_type, date_type, level_type |
| `brand_meta` | 品牌元数据 | brand_name |
| `brand_sales` | 品牌销量 | year, month, brand_id, data_type, date_type, level_type |
| `origin_share_data` | 国别/车系占比（乘联会） | year, month, origin |

- 引擎 InnoDB，charset utf8mb4
- **无 Alembic**：结构变更改 `init_db.sql` + SQLModel 模型，已有库需手动迁移
- Docker 首次初始化：`init_db.sql` 挂到 MySQL `docker-entrypoint-initdb.d`

## 外部数据源

| 数据 | 客户端 | 接口/方式 |
|------|--------|-----------|
| 总体销量 | `YicheOverallClient` | 易车 `carserialsalestrend/search`；零售/产量 × all/nev/bev 六维切片 |
| 品牌销量 | `YicheBrandClient` | 易车 `get_master_sales_history`（按 master_id 批次并发，默认 5/批、8 worker） |
| 品牌元数据 | YAML | `meta_data.yaml` → upsert `brand_meta` |
| 国别占比 | `CpcaClient` | AkShare `car_market_country_cpca()` |

客户端类（`yiche_client.py`）：`YicheOverallClient`、`YicheBrandClient`，组合类 `YicheClient(YicheOverallClient, YicheBrandClient)`；`import_service.py` 实际实例化 `YicheOverallClient()`、`YicheBrandClient()`、`CpcaClient()`（非 `YicheClient`）。易车 retail/production 的 saleType 编码在 overall 与 brand 接口中**顺序相反**（见 `yiche_client.py` 模块注释）。

刷新返回值（销量示例）：`status`、`overall_count`、`brand_count`、`records_count`、`source_errors: { overall, brand }`（`SourceFetchResult.to_error_map()` 生成摘要）。

## 前端 Monorepo 结构

- 业务仅 **`apps/web-tdesign`**；`packages/`、`internal/` 为 Vben 模板公共层，非业务优先改动
- 路径别名 `#/*` → `apps/web-tdesign/src/*`
- 常用脚本（在 `frontend/`）：`pnpm dev:tdesign`、`pnpm build`（=`build:tdesign`）、`pnpm build:workspace`（全仓 Turbo）、`pnpm check:type`、`pnpm check`；构建说明见 `frontend/docs/build-performance.md`

### 销售看板 UI 关键文件

| 用途 | 路径 |
|------|------|
| 双模式视觉 token | `apps/web-tdesign/src/styles/theme.css` |
| 图表主题与交互 | `apps/web-tdesign/src/utils/chart.ts` |
| 同比着色 | `apps/web-tdesign/src/utils/format.ts` |
| 筛选面板 | `apps/web-tdesign/src/components/FilterPanel.vue` |
| 图表/表格区块 | `apps/web-tdesign/src/components/SectionCard.vue` |
| 图表容器 | `apps/web-tdesign/src/components/ChartCard.vue` |
| 加载态 | `apps/web-tdesign/src/components/DataLoadState.vue` |
| 主题偏好 | `apps/web-tdesign/src/preferences.ts` |

### 双模式 CSS 变量（`:root` / `.dark`）

| 变量 | 用途 |
|------|------|
| `--chart-1` … `--chart-8` | 折线/堆叠柱配色 |
| `--chart-axis` / `--chart-grid` | 轴标签与网格线 |
| `--chart-pointer` | axisPointer 指示线 |
| `--chart-tooltip-*` | tooltip 背景/边框/文字 |
| `--sales-destructive` / `--sales-success` | 表格同比红绿 |

### 图表交互约束

- 禁止 `emphasis: { focus: 'series' }`（堆叠柱 hover 时会淡化其他系列）
- 折线/柱系列使用 `emphasis: { disabled: true, focus: 'none' }`；靠 tooltip + axisPointer 反馈
- tooltip 设 `confine: true`，背景/边框读 `--chart-tooltip-*`，保证 light/dark 对比度
- 改配色或交互优先改 `chart.ts`，各页 builder 只负责数据与 legend/grid

### UI 验证清单

1. 三页顶部无重复大标题块（无 PageShell）
2. light/dark 切换后图表轴、tooltip、系列色均清晰
3. 国别堆叠柱 hover 时各系列仍可见、不被淡化
4. 筛选切换、Tab 切换、表格 stripe/hover 正常

## Dev vs Prod

| 项 | 开发 | 生产（Docker） |
|----|------|----------------|
| 前端端口 | 5999 | 8081→容器 8080 |
| API 基址 | `/api`（Vite 代理） | `/api`（nginx 反代 backend:8001） |
| 前端配置来源 | `apps/web-tdesign/.env.*` | `docker/.env` 的 `VITE_*` build-arg |
| 后端配置 | `backend/.env` | compose 注入 `DB_HOST=mysql` 等 |
| 构建 | 本地 `pnpm dev:tdesign` | `Dockerfile.frontend` 内 pnpm build |

生产自检：`window._VBEN_ADMIN_PRO_APP_CONF_.VITE_GLOB_API_URL` 应为 `"/api"`。

## Docker 手动验证清单

1. `docker compose -f docker/docker-compose.yml --env-file docker/.env ps` 三服务 running
2. `curl http://127.0.0.1:8001/docs` → 200
3. `curl http://127.0.0.1:8081/api/v1/market/raw` → JSON
4. 浏览器打开 `http://127.0.0.1:8081/`，三看板可加载
5. 改前端/VITE 后：`docker compose ... build frontend && up -d`

## 故障排查速查

| 现象 | 优先检查 |
|------|----------|
| 库连接失败 | MySQL 进程、`backend/.env` 或 `docker/.env` 密码一致 |
| POST 403 | CSRF Cookie + Header；前端非 GET 自动带 token |
| 品牌销量空 | 是否先刷新 brand-meta；`master_id` 是否存在 |
| 国别占比空/字段缺失 | 是否先刷新 origin；`origin_field_map.yaml` 是否与 AkShare 列名一致 |
| 刷新 partial_failure | 日志 `source_errors`、外网与易车/AkShare 可用性 |
| 页面开但接口错 | Docker 未注入 `VITE_*` → 重建 frontend `--no-cache` |
| 前端代理 404 | 后端是否在 8001；`vite.config.mts` proxy |

## backend 依赖（requirements.txt 摘要）

fastapi、uvicorn、gunicorn、sqlmodel、pymysql、cryptography、akshare、pandas、httpx、python-dotenv、pyyaml
