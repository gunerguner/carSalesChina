# 前端构建性能（carSales）

业务应用为 `apps/web-tdesign`。carSales 对 Vben 默认构建做了精简，**日常与 Docker 请使用 `pnpm build`**（直打 Vite，跳过 Turbo `^build` 链）。

## 做了什么

| 项 | 说明 |
| --- | --- |
| `pnpm build` | `pnpm -F @vben/web-tdesign run build`，不再 `turbo build` 预构建全部 workspace |
| `turbo.json` | `@vben/web-tdesign#build` / `build:analyze` 的 `dependsOn: []` |
| `vite.config.ts` | 关闭 archiver、license、html 二次压缩、devtools、PWA 等 |
| `.env.production` | `VITE_ARCHIVER=false`、`VITE_COMPRESS=none`、`VITE_PWA=false` |

全量 Monorepo 构建（极少需要）：`pnpm run build:workspace`。

## 本地实测（Node v25，冷构建，`turbo --force` vs 优化后直打）

| 指标            | 优化前 | 优化后 |
| --------------- | ------ | ------ |
| 整命令          | ~15s   | ~5s    |
| Vite `built in` | ~2.1s  | ~2.2s  |
| `dist.zip`      | 有     | 无     |

主要节省来自：**不再 tsdown 构建 `@vben-core/*` + 不打 zip**；Vite/Rolldown 本体耗时接近。

## 复现对比

```bash
cd frontend
rm -rf apps/web-tdesign/dist .turbo apps/web-tdesign/node_modules/.vite

# 当前（快）
/usr/bin/time -p pnpm run build

# 旧路径（慢，仅对比用）
/usr/bin/time -p pnpm exec turbo build --filter=@vben/web-tdesign --force
```

传输层压缩由 Docker Nginx `gzip` 负责，勿开启 `VITE_COMPRESS=gzip`（会拖慢构建且与 Nginx 重复）。
