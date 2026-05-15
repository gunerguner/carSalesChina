# 中国汽车销售数据平台

一个用于采集、存储和可视化中国汽车市场销量数据的全栈项目。项目后端基于 FastAPI + SQLModel + MySQL，负责数据采集、入库与分析接口；前端基于 Vue 3、Vite、TDesign 与 Vben Admin Monorepo，提供市场销量、品牌销量与结构分析等页面。

## 功能概览

- **市场销量看板**：查看总体汽车市场按月度、季度、年度维度的销量数据，支持零售/产量口径以及全部/新能源/纯电等级别。
- **品牌销量看板**：维护品牌元数据，并按品牌查看全周期销量趋势。
- **数据分析看板**：提供新能源渗透率、纯电在新能源中的占比趋势、国别/车系占比趋势等分析能力。
- **数据采集管理**：通过管理接口触发销量、品牌元数据、国别占比数据刷新。
- **本地开发代理**：前端开发环境将 `/api` 请求代理到本地 FastAPI 服务。

## 技术栈

### 后端

- Python 3.10+
- FastAPI
- Uvicorn
- SQLModel / SQLAlchemy
- MySQL / PyMySQL
- AkShare、Pandas、HTTPX、PyYAML

### 前端

- Node.js `^20.19.0 || ^22.18.0 || ^24.0.0`
- pnpm `>=10.0.0`
- Vue 3 + Vite
- TDesign Vue Next
- Vben Admin Monorepo
- Pinia、Vue Router、ECharts、Turbo

## 数据来源

本项目的数据采集由后端 `backend/backend/services/import_service.py` 统一编排，当前使用的数据来源如下：

| 数据类型 | 来源 | 采集方式 | 入库表 | 说明 |
| --- | --- | --- | --- | --- |
| 总体销量 | 易车销量趋势接口 | `YicheClient.fetch_all()` 拉取月度数据 | `sales_data` | 覆盖零售、产量口径，以及全部、新能源、纯电级别；字段会标准化为 `year`、`month`、`sales`、`data_type`、`date_type`、`level_type`。 |
| 品牌销量 | 易车品牌销量历史接口 | `YicheClient.fetch_brand_sales()` 按品牌 `master_id` 分批拉取 | `brand_sales` | 仅零售、产量口径及新能源/纯电等月度记录（不采集批发口径）。 |
| 品牌元数据 | 仓库内置 YAML | 读取 `backend/backend/meta_data.yaml` | `brand_meta` | 维护品牌中文名、英文标识与易车 `master_id` 映射，是品牌销量采集的基础数据。 |
| 国别/车系占比 | 乘联会数据（通过 AkShare） | `CpcaClient.get_country_data()` 调用 `ak.car_market_country_cpca()` | `origin_share_data` | 用于自主、德系、日系、美系、欧系、韩系等车系/国别占比分析。 |

> 注意：外部数据源接口可能调整参数、签名、字段结构或访问限制；若刷新数据失败，请优先查看采集日志和后端日志，并检查网络连通性与数据源可用性。

## 目录结构

```text
.
├── backend/
│   ├── backend/
│   │   ├── core/             # 数据库与日志基础设施
│   │   ├── models/           # SQLModel 数据模型
│   │   ├── routers/          # FastAPI 路由
│   │   ├── schemas/          # 请求/响应结构
│   │   ├── services/         # 业务逻辑与数据采集编排
│   │   ├── sources/          # 外部数据源客户端
│   │   ├── config.py         # 环境变量配置
│   │   └── main.py           # FastAPI 应用入口
│   ├── init_db.sql           # MySQL 初始化脚本
│   ├── requirements.txt      # Python 依赖
│   └── .env.example          # 后端环境变量示例
├── frontend/
│   ├── apps/web-tdesign/     # 业务前端应用
│   ├── packages/             # Vben 工作区公共包
│   ├── internal/             # 构建、配置、脚手架内部包
│   ├── package.json          # 前端根脚本
│   └── pnpm-workspace.yaml   # pnpm workspace 配置
├── lefthook.yml
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

4. 确保开发环境可以访问项目依赖源以及外部数据源接口。

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

## 前端启动

```bash
cd frontend
pnpm install
pnpm dev:tdesign
```

前端开发服务默认端口为 `5999`，开发环境接口地址为 `/api`，并由 Vite 代理到 `http://localhost:8001`。

常用脚本：

```bash
# 启动 TDesign 前端应用
pnpm dev:tdesign

# 构建 TDesign 前端应用
pnpm build:tdesign

# 类型检查
pnpm check:type

# 全量前端检查
pnpm check
```

## 数据初始化与刷新流程

建议首次启动后按以下顺序刷新数据：

1. 刷新品牌元数据。
2. 刷新总体销量与品牌销量数据。
3. 刷新国别/车系占比数据。

可通过 OpenAPI 文档调用，也可使用 `curl`：

```bash
# 品牌元数据
curl -X POST http://localhost:8001/api/v1/admin/data/refresh/brand-meta

# 总体销量 + 品牌销量
curl -X POST http://localhost:8001/api/v1/admin/data/refresh/sales

# 国别/车系占比
curl -X POST http://localhost:8001/api/v1/admin/data/refresh/origin
```

> 数据刷新会访问外部数据源，耗时与成功率取决于网络环境、外部接口稳定性和数据源可用性。

## 主要接口

| 模块 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| 市场销量 | GET | `/api/v1/market/raw` | 返回全量月度原始市场数据，供前端本地筛选与聚合 |
| 品牌 | GET | `/api/v1/brands/meta/all` | 返回全部品牌元数据 |
| 品牌 | GET | `/api/v1/brands/trend-all-periods` | 返回指定品牌的全周期销量趋势 |
| 分析 | GET | `/api/v1/analysis/nev-share/trend` | 新能源渗透率趋势 |
| 分析 | GET | `/api/v1/analysis/nev-breakdown` | 纯电在新能源中占比（按同期纯电、新能源销量计算） |
| 分析 | GET | `/api/v1/analysis/origin-share/trend` | 国别/车系占比趋势 |
| 管理 | POST | `/api/v1/admin/data/refresh/sales` | 刷新总体销量与品牌销量 |
| 管理 | POST | `/api/v1/admin/data/refresh/brand-meta` | 刷新品牌元数据 |
| 管理 | POST | `/api/v1/admin/data/refresh/origin` | 刷新国别/车系占比数据 |

## 前端页面

| 路由 | 页面 | 说明 |
| --- | --- | --- |
| `/market-sales` | 市场销量 | 总体销量趋势、表格与多维筛选 |
| `/brand-sales` | 品牌销量 | 品牌选择、销量趋势图与明细表 |
| `/data-analysis` | 数据分析 | 新能源渗透率、纯电在新能源中占比、国别/车系占比分析 |

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
| `LOG_DIR` | `<仓库根>/logs` | 可选日志目录 |

### 前端环境变量

前端应用环境变量位于 `frontend/apps/web-tdesign/.env.*`。开发环境常用变量：

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `VITE_PORT` | `5999` | 前端开发服务端口 |
| `VITE_BASE` | `/` | 应用基础路径 |
| `VITE_GLOB_API_URL` | `/api` | 接口基础地址 |
| `VITE_NITRO_MOCK` | `false` | 是否开启 Nitro Mock |
| `VITE_DEVTOOLS` | `false` | 是否开启 devtools |
| `VITE_APP_TITLE` | `中国市场汽车销量` | 应用标题 |

## 开发建议

- 后端新增接口时，将路由放在 `backend/backend/routers/`，业务逻辑放在 `backend/backend/services/`。
- 后端新增表结构时，同步更新 SQLModel 模型与 `backend/init_db.sql`。
- 前端业务页面集中在 `frontend/apps/web-tdesign/src/views/sales/`。
- 前端接口封装集中在 `frontend/apps/web-tdesign/src/api/sales/`。
- 生产环境请将前端 `VITE_GLOB_API_URL` 指向真实后端地址或配置反向代理。

## 故障排查

- **数据库连接失败**：检查 MySQL 是否启动、账号密码是否正确，以及 `.env` 是否位于 `backend/` 目录。
- **前端请求 404 或代理失败**：确认后端运行在 `http://localhost:8001`，并检查 Vite 代理配置。
- **数据刷新为空或失败**：检查外部网络连通性、外部数据源接口是否可用，并查看日志文件。
- **前端依赖安装失败**：确认 Node.js 与 pnpm 版本符合要求，并检查 npm registry 网络可用性。

## 许可证

前端模板继承 Vben Admin 相关 MIT 许可文件；项目业务代码请根据实际发布策略补充统一许可证说明。
