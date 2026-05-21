---
name: carsales-project
description: carSales 中国汽车销售数据平台参考：FastAPI + SQLModel + MySQL 后端、Vue 3 + Vben Admin + TDesign 前端、易车/乘联会数据采集与本地聚合看板。在 carSales 仓库内改功能、修 bug、加 API、动数据刷新/前端图表或 Docker 部署时使用。
disable-model-invocation: false
---

# carSales 项目参考

采集、存储、分析与可视化中国汽车市场销量数据的全栈项目。

## 仓库布局

```
carSales/                     # Git 根
├── README.md                 # 产品说明、接口、本地启动
├── backend/
│   ├── backend/              # FastAPI 应用包
│   │   ├── core/             # 数据库、CSRF、异常、日志
│   │   ├── models/           # SQLModel 模型
│   │   ├── routers/          # 路由（market/brand/analysis/admin）
│   │   ├── schemas/          # 请求/响应结构
│   │   ├── services/         # 业务与 import 编排
│   │   ├── sources/          # 易车、乘联会客户端
│   │   ├── meta_data.yaml    # 品牌元数据（master_id 映射）
│   │   └── origin_field_map.yaml
│   ├── init_db.sql           # MySQL 建表（唯一 schema 来源）
│   ├── requirements.txt
│   └── .env.example
├── frontend/                 # Vben Admin Monorepo
│   ├── apps/web-tdesign/     # 业务前端（唯一业务 app）
│   ├── packages/             # 工作区公共包
│   └── package.json
└── docker/                   # Compose、Dockerfile、nginx、.env.example
```

版本：前端 Monorepo **5.7.0**（`frontend/package.json`）；后端 FastAPI app **1.0.0**（`backend/backend/main.py`）。

## 技术栈

| 层 | 技术 |
|----|------|
| 后端 | Python ≥3.10，FastAPI，SQLModel/SQLAlchemy，Uvicorn/Gunicorn |
| 数据库 | **MySQL 8.x**（PyMySQL）；**无 Redis**（`.env.example` 中 REDIS 未使用） |
| 外部源 | 易车 HTTP API（`yiche_client.py`）；乘联会 via AkShare（`cpca_client.py`） |
| 前端 | Vue 3 + Vite，TDesign Vue Next，Vben Admin Monorepo，Pinia，ECharts |
| 包管理 | pnpm ≥10（`packageManager: pnpm@10.33.0`），Node ^20.19 \|\| ^22.18 \|\| ^24 |
| 部署 | Docker 三服务：mysql、backend、frontend（Nginx 8080） |

## 架构要点

**请求路径**：Vue SPA → `/api/*` → FastAPI routers → services → MySQL；管理刷新经 `import_service` → `sources/`。

**统一响应**：`{ code, message, data }`；成功 `code=0`。封装：`schemas/response.py` 的 `success()` / `error()`。

**CSRF**：`CSRFCookieMiddleware` 下发 `csrf_token` Cookie；非 GET 管理接口需 `X-CSRF-Token` 与 Cookie 一致（`core/csrf.py`）。前端 `api/request.ts` 自动注入。

**错误码**：`core/error_codes.py`（1001 校验、1002 权限、2001 外部源、3001 数据库、9000 内部）。

**数据刷新**：`import_service._batch_upsert` 用 MySQL `ON DUPLICATE KEY UPDATE`；外部源返回 `SourceFetchResult`（`records`/`ok`/`errors`）；销量刷新可返回 `success` / `partial_failure` / `failed`。

```mermaid
flowchart LR
  Vue[web-tdesign :5999] -->|proxy /api| FastAPI[FastAPI :8001]
  FastAPI --> MySQL[(MySQL)]
  FastAPI --> Yiche[易车 API]
  FastAPI --> Cpca[AkShare 乘联会]
```

## 业务域（已实现）

| 域 | 关键文件 | 说明 |
|----|----------|------|
| 市场销量 | `market_service.py`，`views/sales/market/` | `GET /api/v1/market/raw` 一次拉全量月度数据，前端 `marketDataUtils.ts` 本地筛选/季年聚合 |
| 品牌销量 | `brand_service.py`，`views/sales/brand/` | 最多 3 品牌对比；依赖 `brand_meta.master_id` |
| 数据分析 | `analysis_service.py`，`views/sales/analysis/` | 新能源渗透率、纯电占新能源比、国别/车系份额 |
| 数据刷新 | `import_service.py`，`routers/admin.py` | 品牌元数据 → 总体+品牌销量 → 国别占比（顺序有依赖） |
| 品牌元数据 | `meta_data.yaml` → `brand_meta` | YAML 维护中文名、英文标识、易车 master_id |

**维度枚举**：`data_type` retail/production；`level_type` all/nev/bev；`date_type` monthly/quarterly/yearly（库表支持，采集以月度为主）。

## 修改导航（最常改哪里）

| 目标 | 改动位置 |
|------|----------|
| 新读 API | `routers/*.py` → `services/*.py` → `schemas/*.py` → `frontend/apps/web-tdesign/src/api/sales/` |
| 新刷新/写 API | 同上 + `import_service.py`；路由加 `Depends(verify_csrf)` |
| 新外部源 | `sources/` 新客户端，返回 `SourceFetchResult` |
| 新表/字段 | `models/` + **`init_db.sql` 唯一索引**（upsert 依赖） |
| 新前端页 | `router/routes/modules/sales.ts` + `views/sales/` + `locales/langs/*/sales.json` |
| 市场本地聚合 | `marketDataUtils.ts`（优先复用，勿为每个筛选项打 API） |
| 图表工具 | `utils/chart.ts`、`utils/format.ts`、`utils/period.ts` |
| 管理刷新 UI | `api/admin.ts`；超时 5 分钟 |
| 部署/静态/API 404 | 改前端后须 **重建 frontend 镜像**；`docker/nginx.conf` 反代 `/api` → backend:8001 |

## 本地开发

| 终端 | 命令 | 端口 |
|------|------|------|
| MySQL | `mysql -u root -p < backend/init_db.sql` | 3306 |
| 后端 | `cd backend && source .venv/bin/activate && python -m backend.main` | **8001** |
| 前端 | `cd frontend && pnpm install && pnpm dev:tdesign` | **5999**（代理 `/api` → 8001） |

**环境变量**（`backend/.env`）：`DB_*`、`FASTAPI_PORT`、`LOG_LEVEL`、`LOG_DIR`。

**前端环境**（`frontend/apps/web-tdesign/.env.*`）：`VITE_GLOB_API_URL=/api`、`VITE_PORT=5999` 等。

## 数据初始化顺序

1. `POST /api/v1/admin/data/refresh/brand-meta`
2. `POST /api/v1/admin/data/refresh/sales`
3. `POST /api/v1/admin/data/refresh/origin`

OpenAPI：`http://localhost:8001/docs`。curl 需先取 `csrf_token` Cookie 再设 `X-CSRF-Token`。

## Docker 部署要点

- 三服务：**mysql**、**backend**（Gunicorn 8001）、**frontend**（Nginx **8080** → 宿主机默认 **8081**）
- 配置以 **`docker/.env`** 为准；`VITE_*` 在 **build-arg** 打进镜像，改后须 `build frontend`
- 首次启动挂载 `init_db.sql`；**mysql_data 卷已存在时不会重跑**
- 同机部署 stockManager 时设 `COMPOSE_PROJECT_NAME=carsales`（默认已给出）
- 详见 [docker/README.md](../../../docker/README.md)

## API 一览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/market/raw` | 全量月度市场原始数据 |
| GET | `/api/v1/brands/meta/all` | 全部品牌元数据 |
| GET | `/api/v1/brands/trend-all-periods` | `brand_names`（逗号，≤3）、`data_type` |
| GET | `/api/v1/analysis/nev-share/trend` | `years` 1–10、`granularity` monthly/yearly |
| GET | `/api/v1/analysis/nev-breakdown` | 纯电占新能源比 + 估算插混 |
| GET | `/api/v1/analysis/origin-share/trend` | 国别/车系份额 |
| POST | `/api/v1/admin/data/refresh/brand-meta` | CSRF |
| POST | `/api/v1/admin/data/refresh/sales` | CSRF |
| POST | `/api/v1/admin/data/refresh/origin` | CSRF |

## 前端路由

| 路径 | 页面 |
|------|------|
| `/market-sales` | 市场销量 |
| `/brand-sales` | 品牌销量 |
| `/data-analysis` | 数据分析 |

## 测试

**无自动化单元测试**。改完后手动验证：三看板加载 → 筛选/聚合 → 管理刷新（若有 UI）→ Docker 下 `/api` 反代。前端可跑 `pnpm check:type`、`pnpm lint`。

## 编码约定

- 路由薄、逻辑在 `services/`；管理写操作用 `@handle_try_catch_action`
- 新增外部源勿在 router 直接 httpx，走 `sources/` + `SourceFetchResult`
- 表结构变更同步 `models/` 与 `init_db.sql`，检查 UNIQUE 与 upsert 字段一致
- 前端 API 基址来自 `VITE_GLOB_API_URL`；生产 Docker 默认 `/api`（同源 nginx 反代）
- 业务文案 i18n：`locales/langs/zh-CN/sales.json`、`en-US/sales.json`
- **无用户登录**；仅 CSRF 保护管理 POST

## 更多细节

- 关键文件索引、数据库表、Docker 检查清单：[reference.md](reference.md)
- 部署与排障：`docker/README.md`、根目录 `README.md`
