# carSales Docker 部署

所有 Compose 与镜像定义集中在 **`docker/`** 目录（在 Cursor 中可用 `@docker` 引用）。正式部署以本目录为准。

## 运行时版本

| 组件 | 说明 |
|------|------|
| MySQL | `mysql:9.0`（见 `docker-compose.yml`） |
| 前端构建 | `node:22-slim`（见 `Dockerfile.frontend`） |
| 后端运行 | `python:3.13-slim`（见 `Dockerfile.backend`） |

前端仓库根 `package.json` 的 `engines.node` 可能与容器内 Node 版本不完全一致：**容器内构建以 `Dockerfile.frontend` 为准**。

## 目录说明

| 文件 | 作用 |
|------|------|
| `docker-compose.yml` | `mysql`、`backend`、`frontend` 三服务编排；`build.context` 为仓库根，`dockerfile` 为 `docker/Dockerfile.*` |
| `Dockerfile.backend` | FastAPI + Gunicorn/Uvicorn Worker |
| `Dockerfile.frontend` | `turbo prune` 拆依赖层 + pnpm store 缓存 + 构建 `web-tdesign` + `nginx:stable-alpine` |
| `gunicorn.docker.conf.py` | 容器内 Gunicorn：监听 `0.0.0.0:8001`，日志输出 stdout/stderr |
| `nginx.conf` | 前端容器监听 **8080**（非 80）；`/api` 反代至 `http://backend:8001` |
| `.env.example` | 环境变量模板，复制为 `.env` 后修改 |

仓库根目录的 **`.dockerignore`** 在构建 `context: ..`（仓库根）时生效，用于排除 `node_modules` 等，加快构建。

## 获取代码

镜像构建使用的是 **本机（或 CI 工作目录）里当前工作区的文件**，`Dockerfile` 内不会执行 `git clone`。部署前请先把仓库放到目标机器上，例如：

```bash
git clone <你的仓库 URL> carSales
cd carSales
```

后续在**仓库根目录**（即含 `backend/`、`frontend/`、`docker/` 的那一层）执行下文中的 `docker compose` 命令即可。

## 前置条件

- 已安装 [Docker](https://docs.docker.com/get-docker/) 与 [Docker Compose V2](https://docs.docker.com/compose/)
- 首次启动会执行 `../backend/init_db.sql` 初始化库表（挂载到 MySQL `docker-entrypoint-initdb.d`）。**数据卷 `mysql_data` 已存在时不会再次执行**；若需重建库，请自行备份后删除 volume。

## 配置

1. 复制环境变量文件：

   ```bash
   cp docker/.env.example docker/.env
   ```

2. 编辑 `docker/.env`，至少设置：

   - **`COMPOSE_PROJECT_NAME`**：默认 `carsales`（`.env.example` 已给出）。与 **stockManager** 等同机部署时**勿删**；与 stockManager 的 `stockmanager` 区分开，避免两套栈互相顶替。
   - `MYSQL_ROOT_PASSWORD`
   - `DB_PASSWORD`（与 `MYSQL_USER` / `MYSQL_DATABASE` 对应的应用用户密码）
   - **`VITE_ADMIN_REFRESH_CONFIRM_CODE`**：页面右上角「刷新全部数据」的二次确认码（构建时写入前端 JS，**务必改成非默认值**）

3. 应用连接数据库：后端容器内使用 `DB_HOST=mysql`（已在 `docker-compose.yml` 中写死），用户名与库名与 `DB_USER`、`DB_NAME` 一致。

## 数据库：要手动进 MySQL 建用户吗？还是只配 env？

**正常情况下只配 `docker/.env` 即可，不必先登录 MySQL 手工建用户。**

- `docker-compose.yml` 会把 `docker/.env` 里的变量传给官方 `mysql` 镜像：`MYSQL_ROOT_PASSWORD`、`MYSQL_DATABASE`（来自 `DB_NAME`）、`MYSQL_USER`（来自 `DB_USER`）、`MYSQL_PASSWORD`（来自 `DB_PASSWORD`）。
- **仅在数据目录为空（第一次创建 `mysql_data` 卷）时**，入口脚本会根据上述变量创建 `root` 密码、业务库、业务用户，并执行挂载的 `init_db.sql` 建表。
- `backend` 服务使用的 `DB_USER` / `DB_PASSWORD` / `DB_NAME` 与 `mysql` 服务上的 `MYSQL_USER` / `MYSQL_PASSWORD` / `MYSQL_DATABASE` **是同一套值**，由同一份 `docker/.env` 提供，因此**不需要**你在库内再建一套账号给后端用。

**例外（需要人工介入的情况）：**

- **卷里已经有旧数据**：改 `docker/.env` 里的密码**不会**自动改掉库里已有账号的密码；要么继续用旧密码（与 `.env` 保持一致），要么进库 `ALTER USER` / 重建用户，要么备份后 `docker volume rm` 对应 volume 再首次初始化（会丢库，谨慎）。
- **想用 root 连库**：官方镜像不允许 `MYSQL_USER=root`；应用侧请用非 root 业务账号（如 `car_sales`）。若你坚持 root，需自行改 compose（不推荐）。

## 启动与停止

在**仓库根目录**执行（推荐显式指定 compose 文件）：

```bash
docker compose -f docker/docker-compose.yml --env-file docker/.env build
docker compose -f docker/docker-compose.yml --env-file docker/.env up -d
```

或在 `docker/` 目录下：

```bash
cd docker
docker compose --env-file .env build
docker compose --env-file .env up -d
```

停止并删除容器（保留数据卷）：

```bash
docker compose -f docker/docker-compose.yml --env-file docker/.env down
```

## 更新代码后重新部署

在**仓库根目录**拉取最新代码，再重新构建并启动（MySQL 使用数据卷，一般**不会**因本次操作丢数据；若 `init_db.sql` 或库结构有变，见上文「数据卷已存在时不会再次执行」及「常见问题」）：

```bash
cd /path/to/carSales   # 换成你本机的仓库路径
git pull               # 或切换到目标分支 / 标签后再部署
```

若 `docker/.env.example` 或 `docker-compose.yml` 有新增变量或说明，可对照更新本地的 `docker/.env`。

重新构建镜像并应用新容器（`mysql` 为官方镜像、无本地 `build`，compose 会跳过或保持其运行）：

```bash
docker compose -f docker/docker-compose.yml --env-file docker/.env build
docker compose -f docker/docker-compose.yml --env-file docker/.env up -d
```

仅改了前端或后端时，可只构建对应服务以节省时间：

```bash
docker compose -f docker/docker-compose.yml --env-file docker/.env build backend frontend
docker compose -f docker/docker-compose.yml --env-file docker/.env up -d
```

怀疑依赖或层缓存导致行为与预期不符时，可对单服务强制不用缓存重建（示例：前端）：

```bash
docker compose -f docker/docker-compose.yml --env-file docker/.env build --no-cache frontend
docker compose -f docker/docker-compose.yml --env-file docker/.env up -d
```

部署后建议执行下文「如何验证」中的检查，并查看 `docker compose ... logs` 确认无报错。

## 如何验证「一切都 OK」

以下命令默认在**仓库根目录**执行，且已准备好 `docker/.env`。若端口改过，请把示例里的 `8001`、`8081` 换成你在 `docker/.env` 中的 `BACKEND_PUBLISH_PORT`、`FRONTEND_PUBLISH_PORT`。

### 1. 容器状态

```bash
docker compose -f docker/docker-compose.yml --env-file docker/.env ps
```

期望：`mysql`、`backend`、`frontend` 均为 `running`（或 `healthy`）。若 `backend` 一直 `starting`，多半是等 MySQL 健康检查或未连上库。

### 2. 看日志（无报错、无反复重启）

```bash
docker compose -f docker/docker-compose.yml --env-file docker/.env logs --tail=80 mysql
docker compose -f docker/docker-compose.yml --env-file docker/.env logs --tail=80 backend
docker compose -f docker/docker-compose.yml --env-file docker/.env logs --tail=80 frontend
```

期望：`mysql` 出现 `ready for connections`；`backend` 无 Traceback、无反复崩溃；`frontend` 无 nginx 致命错误。

### 3. 直连后端（绕过前端 nginx）

```bash
curl -sS -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1:8001/docs
curl -sS "http://127.0.0.1:8001/api/v1/market/raw" | head -c 400
echo
```

期望：第一行 `HTTP 200`；第二行返回 JSON（可能含业务数据或空列表，取决于库内是否有数据），**不应**是连接被拒绝或 5xx。

### 4. 走前端容器（静态页 + `/api` 反代）

```bash
curl -sS -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1:8081/
curl -sS "http://127.0.0.1:8081/api/v1/market/raw" | head -c 400
echo
```

期望：首页 `HTTP 200`；`/api/...` 与上一步直连后端结果一致（说明 `docker/nginx.conf` 反代正常）。

### 5.（可选）在 MySQL 容器内确认库表

在 **bash / zsh** 下将 `docker/.env` 导出到当前 shell（密码中含特殊字符时请在交互式终端中操作，并注意勿泄露）：

```bash
set -a && source docker/.env && set +a
docker compose -f docker/docker-compose.yml --env-file docker/.env exec mysql \
  mysql -u"$DB_USER" -p"$DB_PASSWORD" -e "SHOW TABLES;" "$DB_NAME"
```

期望：能看到 `init_db.sql` 创建的表名（如 `sales_data`、`brand_meta` 等）。

### 6. 浏览器

- 打开 `http://127.0.0.1:8081/`（或宿主机 IP + 映射端口），页面应能加载。
- 打开开发者工具 → 网络，刷新后接口请求应指向同源下的 `/api/...`，且状态码为 2xx（无数据时也可能返回空列表，属正常）。

若某一步失败，优先对照「常见问题」一节，并重点检查：**首次初始化是否成功**（卷是否已存在导致 `init_db.sql` 未再执行）、**`.env` 中密码是否与卷内已有实例一致**。

## 端口与上游统一 Nginx

| 服务 | 容器内端口 | 默认映射到宿主机 |
|------|------------|------------------|
| frontend（nginx） | 8080 | `FRONTEND_PUBLISH_PORT`（默认 8081，与 stockManager 同机部署时避免与 8080 冲突） |
| backend（Gunicorn） | 8001 | `BACKEND_PUBLISH_PORT`（默认 8001） |
| mysql | 3306 | 不映射（仅容器网络内访问） |

前端容器**不使用 80 端口**。在你侧的统一 Nginx 上，按 `server_name` 将流量反代到本机或内网的 **`http://<宿主机>:<FRONTEND_PUBLISH_PORT>`**（默认 **8081**）即可；浏览器仍访问 `/api`，由前端容器内 nginx 转发到 `backend:8001`。

示例（仅供参考，由你方统一 Nginx 维护）：

```nginx
location / {
    proxy_pass http://127.0.0.1:8081;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

## 环境变量：用哪一份？

| 文件 | 谁读 | 说明 |
|------|------|------|
| **`docker/.env`** | `docker compose` | MySQL 密码、端口、`VITE_*` 构建参数等。**部署以它为准。** |
| **`backend/.env`** | 本机 `uvicorn`/IDE 直跑后端 | **容器内 backend 不用此文件**，由 compose 注入 `DB_HOST=mysql` 等。 |
| **`frontend/apps/web-tdesign/.env*`** | 本地 `pnpm dev` / 非 Docker 构建 | Docker 构建时根目录 `.dockerignore` 会排除 `**/.env*`，前端配置靠 **`docker/.env` 的 `VITE_*` + 镜像 build-arg**。 |

改 `docker/.env` 里的 `VITE_*` 后必须 **重新 build frontend**（仅 `up -d` 不会改已打进 JS 的配置）。

## 前端 API 基址与标题

默认 `VITE_GLOB_API_URL=/api`，与容器内 `nginx.conf` 反代一致。标题等见 `docker/.env.example` 中的 `VITE_APP_TITLE`。

**刷新全部数据确认码**：`VITE_ADMIN_REFRESH_CONFIRM_CODE` 在构建时注入前端，点击右上角刷新按钮时需输入与之相同的确认码。改 `docker/.env` 中该值后须 **重新 build frontend**（与上述 `VITE_*` 规则相同）。未配置或仍为示例值 `change-me` 时，页面会提示无法刷新。

**自检（浏览器 F12 → Console）：**

```js
window._VBEN_ADMIN_PRO_APP_CONF_
// 期望含 VITE_GLOB_API_URL: "/api"，勿为 mock 域名或空对象
```

**自检（服务器）：**

```bash
docker exec car-sales-frontend grep -o 'VITE_GLOB_API_URL[^,]*' /usr/share/nginx/html/_app.config.js | head -1
```

## Gunicorn 调优（可选）

在 `docker-compose.yml` 的 `backend.environment` 中可加入：

- `GUNICORN_WORKERS`（默认见 `gunicorn.docker.conf.py`，上限 4）
- `GUNICORN_TIMEOUT`
- `GUNICORN_LOG_LEVEL`

## 前端镜像构建加速

`Dockerfile.frontend` 使用 **BuildKit**（Compose 默认开启）：

1. **`turbo prune @vben/web-tdesign --docker`**：生成 `out/json`（仅 lock + 各 workspace 的 `package.json`）与 `out/full`（裁剪后的源码）。
2. **依赖层**：`out/json` + `pnpm install --ignore-scripts`（避免仅有 `package.json` 时 postinstall `stub` 找不到 `scripts/`）；仅当 lock 变化时失效。
3. **源码层**：`out/full` + `pnpm -r run stub` + `pnpm run build`；**只改 Vue/TS** 时 install 可缓存，多数只重跑 stub + Vite（见 `frontend/docs/build-performance.md`）。

查看各步耗时：`docker build --progress=plain -f docker/Dockerfile.frontend .`（在仓库根执行）。勿滥用 `--no-cache`。

本地 `turbo prune` 产生的 `frontend/out/` 已加入 `.dockerignore`，不会打进构建上下文。

## 常见问题

- **MySQL 健康检查失败**：确认 `MYSQL_ROOT_PASSWORD` 与 `docker/.env` 一致，且首次初始化未因权限/脚本错误中断；可查看 `docker compose logs mysql`。
- **后端连不上库**：确认 `DB_USER` / `DB_PASSWORD` / `DB_NAME` 与 MySQL 服务环境变量一致，且非 `root` 作为 `MYSQL_USER`（镜像限制）。
- **前端接口 404**：确认请求路径以 `/api` 开头，与后端路由前缀一致。
- **页面能开但接口全错、标题为空、反复弹「请求失败」**：多为 Docker 构建未注入 `VITE_*`（`.env` 未打进镜像）。确认 `docker/.env` 含 `VITE_GLOB_API_URL=/api`、`VITE_APP_TITLE`，执行 `build --no-cache frontend` 后 `up -d`；浏览器检查 `window._VBEN_ADMIN_PRO_APP_CONF_`。接口恢复后若仍双份弹窗，拉取最新前端（已去掉与全局拦截器重复的页面级 `message.error`）。
- **刷新全部数据提示「未配置刷新确认码」或确认码始终不对**：确认 `docker/.env` 已设置 `VITE_ADMIN_REFRESH_CONFIRM_CODE`（勿留 `change-me`），并执行 `build frontend` 后 `up -d`；仅改 `.env` 不重建镜像不会生效。
