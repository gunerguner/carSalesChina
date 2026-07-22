# 中国汽车销售数据平台

一个用于采集、存储、分析和可视化中国汽车市场销量数据的全栈项目。后端基于 FastAPI + SQLModel + MySQL，负责外部数据源采集、标准化入库、统一异常响应和分析接口；前端基于 Vue 3、Vite、TDesign 与 Vben Admin Monorepo，提供市场销量、品牌销量与数据分析页面。

## 功能概览

- **市场销量看板**：一次加载全量月度原始市场数据，在前端本地完成筛选、月度明细、季度聚合和年度聚合，支持零售/产量口径以及全部/新能源/纯电级别。
- **品牌销量看板**：读取品牌元数据，支持最多 3 个品牌对比，提供零售/产量切换、月度/季度/年度聚合趋势图和明细表。
- **数据分析看板**：展示新能源渗透率、纯电在新能源中的占比，以及自主、德系、日系、美系、欧系、韩系等国别/车系份额趋势。
- **数据刷新管理**：提供品牌元数据、总体销量 + 品牌销量、国别/车系占比三类刷新接口，写入时使用批量 upsert，支持部分外部源失败时返回 `partial_failure`。
- **安全与错误处理**：后端统一返回 `{ code, message, data }` 响应；非 GET 管理接口启用 CSRF Cookie/Header 校验，前端请求拦截器会自动带上 `X-CSRF-Token`。
- **本地开发代理**：前端开发环境将 `/api` 请求代理到本地 FastAPI 服务 `http://localhost:8001`。

## 技术栈

### 后端

- Python 3.10+
- FastAPI / Uvicorn / Gunicorn
- SQLModel / SQLAlchemy
- MySQL / PyMySQL / cryptography
- AkShare、Pandas、HTTPX、PyYAML、python-dotenv

### 前端

- Node.js `^20.19.0 || ^22.18.0 || ^24.0.0`
- pnpm `>=10.0.0`（当前 `packageManager` 为 `pnpm@10.33.0`）
- Vue 3 + Vite
- TDesign Vue Next
- Vben Admin Monorepo
- Pinia、Vue Router、ECharts、Turbo

## 数据来源与入库模型

本项目的数据采集由 `backend/backend/services/import_service.py` 统一编排，当前使用的数据来源如下：

| 数据类型 | 来源 | 采集方式 | 入库表 | 说明 |
| --- | --- | --- | --- | --- |
| 总体销量 | 易车销量趋势接口 `carserialsalestrend/search` | `YicheOverallClient.fetch_overall_sales()` 按口径与级别逐维度拉取 | `sales_data` | 当前采集月度数据，覆盖零售、产量口径，以及全部、新能源、纯电级别；字段标准化为 `year`、`month`、`sales`、`data_type`、`date_type`、`level_type`。 |
| 品牌销量 | 易车品牌销量历史接口 `get_master_sales_history` | `YicheBrandClient.fetch_brand_sales()` 按 `master_id` 分批并发拉取 | `brand_sales` | 依赖 `brand_meta.master_id`；当前采集零售全部/新能源/纯电，以及产量全部的月度记录，不采集批发口径。 |
| 品牌元数据 | 仓库内置 YAML | 读取 `backend/backend/meta_data.yaml` | `brand_meta` | 维护品牌中文名、英文标识与易车 `master_id` 映射，是品牌销量采集的基础数据。 |
| 国别/车系占比 | 乘联会数据（通过 AkShare） | `CpcaClient.get_country_data()` 调用 `ak.car_market_country_cpca()` | `origin_share_data` | 后端按 `backend/backend/origin_field_map.yaml` 将中文国别映射为前端字段，用于份额趋势分析。 |

> 注意：外部数据源接口可能调整参数、签名、字段结构或访问限制；若刷新数据失败，请优先查看采集日志和后端日志，并检查网络连通性与数据源可用性。

## 目录结构

```text
.
├── backend/
│   ├── backend/
│   │   ├── core/             # 数据库、日志、CSRF、中间件、异常处理等基础设施
│   │   ├── models/           # SQLModel 数据模型
│   │   ├── routers/          # FastAPI 路由
│   │   ├── schemas/          # 请求/响应结构
│   │   ├── services/         # 业务逻辑与数据采集编排
│   │   ├── sources/          # 外部数据源客户端
│   │   ├── config.py         # 环境变量配置
│   │   ├── main.py           # FastAPI 应用入口
│   │   ├── meta_data.yaml    # 品牌元数据
│   │   └── origin_field_map.yaml
│   ├── gunicorn.conf.py      # Gunicorn 部署配置
│   ├── init_db.sql           # MySQL 初始化脚本
│   ├── requirements.txt      # Python 依赖
│   └── .env.example          # 后端环境变量示例
├── frontend/
│   ├── apps/web-tdesign/     # 业务前端应用
│   ├── packages/             # Vben 工作区公共包
│   ├── internal/             # 构建、配置、脚手架内部包
│   ├── package.json          # 前端根脚本
│   └── pnpm-workspace.yaml   # pnpm workspace 配置
└── README.md
```

## 环境准备

1. 安装并启动 MySQL 8.x（或兼容版本）。
2. 安装 Python 3.10+。
3. 安装 Node.js 与 pnpm：

   ```bash
   corepack enable
   corepack prepare pnpm@10.33.0 --activate
   ```

4. 确保开发环境可以访问 Python/npm 依赖源以及易车、乘联会/AkShare 等外部数据源接口。

## 后端启动

### 1. 初始化数据库

```bash
mysql -u root -p < backend/init_db.sql
```

如需使用自定义数据库名、账号或密码，请同步调整后端 `.env`。

### 2. 配置环境变量

```bash
cd backend
cp .env.example .env
```

按需修改 `.env`：

```dotenv
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=xxx
DB_NAME=car_sales
FASTAPI_PORT=8001
LOG_LEVEL=INFO
# LOG_DIR=/var/log/car-sales
```

### 3. 安装依赖并运行服务

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m backend.main
```

服务默认运行在：

- API 地址：`http://localhost:8001`
- OpenAPI 文档：`http://localhost:8001/docs`

如需使用 Gunicorn 部署，可参考 `backend/gunicorn.conf.py`。

## 前端启动

```bash
cd frontend
pnpm install
pnpm dev
```

前端开发服务默认端口为 `5999`，开发环境接口地址为 `/api`，并由 Vite 代理到 `http://localhost:8001`。

常用脚本：

```bash
# 启动 TDesign 前端应用（dev:tdesign 为兼容别名）
pnpm dev

# 构建业务前端（直打 Vite，约 5s；见 frontend/docs/build-performance.md）
pnpm build

# 与 pnpm build 相同（兼容旧命令）
pnpm build:tdesign

# 类型检查
pnpm check:type

# 全量前端检查（循环依赖、依赖、类型、拼写）
pnpm check

# 格式化/代码风格检查
pnpm format
pnpm lint
```

## 数据初始化与刷新流程

建议首次启动后通过管理刷新接口一次性拉取全部数据（品牌元数据 → 销量 → 国别占比，顺序由服务端编排）：

1. 刷新品牌元数据，将 `meta_data.yaml` 中的品牌与易车 `master_id` 写入 `brand_meta`。
2. 刷新总体销量与品牌销量数据；品牌销量依赖上一步中的 `master_id`。
3. 刷新国别/车系占比数据。

前端右上角刷新按钮会打开进度浮层并走 SSE 流式接口。若使用 `curl`，可调用单一 stream 端点（`Accept: text/event-stream`）。由于管理接口启用了 CSRF 校验，直接使用 `curl` 时需要先获取 `csrf_token` Cookie，再把同一个值放入 `X-CSRF-Token` 请求头：

```bash
# 获取 CSRF Cookie
curl -c /tmp/car-sales-cookies.txt http://localhost:8001/docs >/dev/null
CSRF_TOKEN=$(awk '$6 == "csrf_token" { print $7 }' /tmp/car-sales-cookies.txt)

# 全量刷新（SSE 流式进度）
curl -N -b /tmp/car-sales-cookies.txt \
  -H "X-CSRF-Token: ${CSRF_TOKEN}" \
  -H "Accept: text/event-stream" \
  -X POST http://localhost:8001/api/v1/admin/data/refresh/stream
```

前端请求拦截器会从 `csrf_token` Cookie 读取 token，并在非 GET 请求中自动设置 `X-CSRF-Token`，无需手动处理。

> 数据刷新会访问外部数据源，耗时与成功率取决于网络环境、外部接口稳定性和数据源可用性。销量刷新接口可能返回 `success`、`partial_failure` 或 `failed`，可通过 `source_errors` 查看外部源错误摘要。

## 主要接口

所有业务接口默认包裹在统一响应结构中：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

| 模块 | 方法 | 路径 | 查询参数/请求说明 | 说明 |
| --- | --- | --- | --- | --- |
| 市场销量 | GET | `/api/v1/market/raw` | 无 | 返回全量月度原始市场数据，供前端本地筛选与聚合 |
| 品牌 | GET | `/api/v1/brands/meta/all` | 无 | 返回全部品牌元数据 |
| 品牌 | GET | `/api/v1/brands/trend-all-periods` | `brand_names`：逗号分隔，最多 3 个；`data_type`：`retail`/`production` | 返回指定品牌的全周期月度销量趋势 |
| 分析 | GET | `/api/v1/analysis/nev-share/trend` | `years`：1-10，默认 3；`granularity`：`monthly`/`yearly` | 新能源渗透率趋势 |
| 分析 | GET | `/api/v1/analysis/nev-breakdown` | `years`：1-10，默认 3；`granularity`：`monthly`/`yearly` | 纯电在新能源中占比，另返回估算插混销量与占比 |
| 分析 | GET | `/api/v1/analysis/origin-share/trend` | `years`：1-10，默认 3；`granularity`：`monthly`/`yearly` | 国别/车系占比趋势 |
| 管理 | POST | `/api/v1/admin/data/refresh/stream` | 需要 CSRF Cookie/Header；`Accept: text/event-stream` | SSE 流式全量刷新（品牌元数据 → 销量 → 国别占比） |

## 前端页面

| 路由 | 页面 | 说明 |
| --- | --- | --- |
| `/market` | 市场销量 | 总体销量趋势、月度明细、季度聚合、年度汇总，多维筛选支持零售/产量与全部/新能源/纯电 |
| `/brand` | 品牌销量 | 品牌选择与最多 3 品牌对比，支持零售/产量和月度/季度/年度粒度 |
| `/nev` | NEV 覆盖率 | 新能源渗透率、纯电占新能源比例 |
| `/origin` | 车系占比 | 国别/车系份额趋势 |

## 配置说明

### 后端 `.env`

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `DB_HOST` | `localhost` | MySQL 主机 |
| `DB_PORT` | `3306` | MySQL 端口 |
| `DB_USER` | `root` | MySQL 用户名 |
| `DB_PASSWORD` | 空 | MySQL 密码 |
| `DB_NAME` | `car_sales` | 数据库名称 |
| `FASTAPI_PORT` | `8001` | FastAPI 服务端口 |
| `LOG_LEVEL` | `INFO` | 控制台日志级别 |
| `LOG_DIR` | `<启动目录>/logs` | 可选日志目录；未设置时默认写入启动目录下的 `logs` |

> `.env.example` 中保留了 `REDIS_HOST`、`REDIS_PORT` 示例变量，但当前后端配置未使用 Redis。

### 前端环境变量

前端应用环境变量位于 `frontend/apps/web-tdesign/.env.*`。开发环境常用变量：

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `VITE_PORT` | `5999` | 前端开发服务端口 |
| `VITE_BASE` | `/` | 应用基础路径 |
| `VITE_GLOB_API_URL` | `/api` | 接口基础地址 |
| `VITE_NITRO_MOCK` | `false` | 是否开启 Nitro Mock |
| `VITE_DEVTOOLS` | `false` | 是否开启 devtools |
| `VITE_ARCHIVER` | `false` | 是否生成 `dist.zip`（建议关闭以加快构建） |
| `VITE_COMPRESS` | `none` | 构建期 gzip/brotli（生产由 Nginx gzip，保持 none） |
| `VITE_PWA` | `false` | 是否开启 PWA |
| `VITE_INJECT_APP_LOADING` | `true` | 是否注入全局 loading |
| `VITE_APP_TITLE` | `中国市场汽车销量` | 应用标题 |

## 开发建议

- 后端新增接口时，将路由放在 `backend/backend/routers/`，业务逻辑放在 `backend/backend/services/`，请求参数和响应结构放在 `backend/backend/schemas/`。
- 后端新增表结构时，同步更新 SQLModel 模型与 `backend/init_db.sql`，并检查唯一索引是否满足 upsert 需求。
- 新增外部数据源时，优先在 `backend/backend/sources/` 中封装客户端，并通过 `SourceFetchResult` 返回 `records`、`ok` 和 `errors`，便于刷新接口汇总状态。
- 前端业务页面集中在 `frontend/apps/web-tdesign/src/views/sales/`。
- 前端接口封装集中在 `frontend/apps/web-tdesign/src/api/sales/`，管理类刷新接口位于 `frontend/apps/web-tdesign/src/api/admin.ts`。
- 市场销量页面优先复用 `marketDataUtils.ts` 中的本地聚合逻辑，避免每个筛选项都请求后端。
- 生产环境请将前端 `VITE_GLOB_API_URL` 指向真实后端地址，或配置反向代理把 `/api` 转发到 FastAPI 服务。

## 故障排查

- **数据库连接失败**：检查 MySQL 是否启动、账号密码是否正确，以及 `.env` 是否位于 `backend/` 目录。
- **前端请求 404 或代理失败**：确认后端运行在 `http://localhost:8001`，并检查 `frontend/apps/web-tdesign/vite.config.ts` 中的代理配置。
- **POST 管理接口返回 403**：确认请求携带了 `csrf_token` Cookie，并在 `X-CSRF-Token` 请求头中传入相同值；前端页面内请求会自动处理。
- **数据刷新为空或失败**：检查外部网络连通性、外部数据源接口是否可用，并查看日志文件中的 `source_errors`。
- **品牌销量为空**：先确认已经刷新品牌元数据，并且 `brand_meta` 中目标品牌存在有效 `master_id`。
- **前端依赖安装失败**：确认 Node.js 与 pnpm 版本符合要求，并检查 npm registry 网络可用性。

## 许可证

前端模板继承 Vben Admin 相关 MIT 许可文件；项目业务代码请根据实际发布策略补充统一许可证说明。
