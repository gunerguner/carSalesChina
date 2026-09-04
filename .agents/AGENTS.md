# Agent 约定

给 AI 看的仓库约定与技能都在 **`.agents/`**（不要写到仓库根）。本文件是完成标准，项目细节在 `skills/carsales-project/SKILL.md`。

Cursor 的 `.cursor/rules/run-tests.mdc` 只是 always-apply 钩子，约定以本文件为准。

## 较大改动必须跑测试

完成前必须用 Shell **真正执行测试**，不能只告诉用户去跑。失败则修到全绿。没跑测试不得声称完成。

命中任一条即须跑测：

- 改了业务逻辑、API、数据刷新/SSE、图表/聚合、校验、错误映射
- 一次改动触及多个源文件
- 新增功能或修 bug（非纯文案/注释）

纯文档、注释、格式、`.md` / skill 文案：可跳过测试。

在**仓库根**执行：

| 改动范围 | 命令 |
|------|------|
| 前后端都动、或拿不准 | `make test` |
| 只动 `backend/` | `make test-backend` |
| 只动 `frontend/` 业务代码 | `make test-frontend` |

不要用 `make check` 代替回归（lint 有已知 oxfmt 历史漂移）。

新增或修改逻辑时同步补/改用例：

- 后端：`backend/tests/`
- 前端：`frontend/apps/web-tdesign/tests/`（与 `src/` 镜像，不要把 `*.test.ts` 放进 `src/`）

禁止用 `!` 非空断言。CI：`.github/workflows/test.yml`。
