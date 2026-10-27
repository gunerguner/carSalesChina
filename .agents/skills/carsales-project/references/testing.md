# 自动化测试

改业务代码后的回归入口。给 Agent 看；命令与用例位置以本文件为准。完成标准（什么算「较大改动、必须跑测」）见仓库根 `.agents/AGENTS.md`。

## 命令

仓库根：

```bash
make test            # 全量：后端 pytest（250 用例）+ 前端 vitest（133 用例 / 18 文件）
make test-backend    # 仅后端（~1s，SQLite 内存库，无需 MySQL）
make test-frontend   # 仅前端（turbo run test）
make test-cov        # 同 test + 覆盖率：后端 fail-under=90（当前 ~99%）；前端只出报告、不设门槛
make check           # make test + 前端 lint/typecheck
```

直连方式：

```bash
# 后端
cd backend && .venv/bin/python -m pytest

# 前端
cd frontend && pnpm test
```

首次环境准备：

```bash
# 后端测试依赖（无 .venv 时先 python3 -m venv .venv）
cd backend && .venv/bin/pip install -r requirements-dev.txt

# 前端依赖
cd frontend && pnpm install
```

前端 lint/typecheck（`pnpm lint`、`pnpm check:type`）需要 **Node ≥22.18**（oxfmt/oxlint 的 TS 配置加载限制，`.node-version` 为 22.22.0）；`make test` 本身 Node 20 也能跑。

## 用例位置

| 层 | 用例位置 | 被测代码 |
|----|----------|----------|
| 后端 | `backend/tests/`（`conftest.py` + 15 个 `test_*.py`） | `backend/backend/` |
| 前端 | `apps/web-tdesign/tests/`（与 `src/` 镜像的独立测试树） | `apps/web-tdesign/src/` |

- 前端 vitest 只收集 `tests/**/*.test.ts`（`apps/web-tdesign/vitest.config.ts`），**不要**把 `*.test.ts` 放进 `src/`，也不要建别的目录
- 断言取值用 `#tests/testUtils` 的 `itemAt` / `mustGet`（别处不要再造）
- 覆盖率只统计 `src/**/*.ts`（不含 Vue SFC）：`pnpm -F @vben/web-tdesign run test:cov`
- 后端覆盖率配置在 `backend/pyproject.toml`（`[tool.coverage.*]`）；`database.py` / `main.lifespan` 绑定生产 MySQL，单测刻意不覆盖

后端测试基础设施（`conftest.py`）：SQLite 内存库 + `StaticPool`（TestClient 线程安全），**不连 MySQL**；`_batch_upsert` 的 MySQL 方言 SQL 用编译断言守护；外部源（易车 httpx、akshare）一律 monkeypatch，禁止真实外网请求。

## 何时跑、跑哪个

改动触及下面任一类，结束前跑对应回归；拿不准就 `make test`：

| 改动 | 回归 |
|------|------|
| `backend/backend/` 任意源码 | `make test-backend` |
| 刷新/SSE/外部源（`import_service`、`refresh_orchestrator`、`sources/`） | 另核对 `tests/test_import_service.py`、`test_refresh_orchestrator.py`、`test_sources_*.py` |
| 异常映射 / CSRF / API 信封 | `tests/test_exception_handlers.py`、`test_api_admin.py` |
| 前端市场聚合 / 图表 | `tests/views/market/` |
| 前端 NEV / 车系 / 品牌 builder | `tests/views/{nev,origin,brand}/` |
| 前端进度状态机 / SSE 帧解析 | `tests/composables/useAdminDataRefresh.types.test.ts`、`tests/api/admin.test.ts` |
| 前端数据加载 / 去重 | `tests/composables/useFetchOnce.test.ts` |
| 通用前端 utils | `tests/utils/*.test.ts` |

只改 `.md`、`.agents/`、`docker/`、注释、纯文案可跳过。新增或修改逻辑须同步补/改对应用例，禁止只删断言换绿。

## 硬约束（lint 强制）

- 禁止 `!` 非空断言（oxlint）；tsconfig 又开了 `noUncheckedIndexedAccess`——测试里数组/Map 取值用 `itemAt` / `mustGet` 解包
- 数字字面量 ≥5 位加分隔符（`10000` → `10_000`，unicorn 规则）
- import 顺序由 perfectionist 规则约束，写完对测试文件跑一次 `pnpm exec eslint --fix "apps/web-tdesign/tests/**/*.test.ts"`
- i18n 一律注入假 `t`（`(key) => key`），不 import 真实 `$t`；`.vue` 组件测试 mock `#/locales`
- 测试名里不要出现未插值的 `${...}` 字符串（no-template-curly-in-string）

## 已知例外与边界

- `pnpm lint` 的 oxfmt 阶段会报 `apps/web-tdesign/src/views/market/components/marketSalesTable.ts` 格式漂移——git HEAD 即如此，勿顺手全仓格式化
- 回归判定用 `make test`，**不要**用 `make check`（含 lint，会被上述历史漂移卡住）
- 不测：真实外网拉数（易车/乘联会）、真实 MySQL、Docker 部署链路（见 `docker/README.md` 手动清单）
- 时钟敏感：`_start_year` 依赖 `datetime.now()`，用例以当前年为锚构造数据（`analysis_dataset` fixture）
- 无 GitHub Actions、无 pre-commit/hook 自动触发；回归靠 Agent 在完成前主动执行，全绿才算完成
