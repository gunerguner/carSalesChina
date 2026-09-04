# carSalesChina 统一回归入口
# 用法：make test（前后端全量） / make test-backend / make test-frontend / make test-cov / make check

PY ?= backend/.venv/bin/python
PNPM ?= pnpm

.PHONY: test test-backend test-frontend test-cov test-backend-cov test-frontend-cov check help

help: ## 列出可用命令
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

test: test-backend test-frontend ## 前后端全量测试（AI coding 回归首选）

test-backend: ## 后端 pytest（秒级，无覆盖率）
	@if [ ! -x backend/.venv/bin/python ]; then \
		echo "缺少 backend/.venv，请先执行: cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt"; \
		exit 1; \
	fi
	cd backend && .venv/bin/python -m pytest

test-frontend: ## 前端 vitest（turbo run test）
	cd frontend && $(PNPM) test

test-cov: test-backend-cov test-frontend-cov ## 前后端测试 + 覆盖率报告

test-backend-cov: ## 后端 pytest + coverage（fail-under=90）
	@if [ ! -x backend/.venv/bin/python ]; then \
		echo "缺少 backend/.venv，请先执行: cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt"; \
		exit 1; \
	fi
	cd backend && .venv/bin/python -m pytest --cov=backend --cov-report=term-missing --cov-fail-under=90

test-frontend-cov: ## 前端 vitest + coverage（报告，不设门槛）
	cd frontend && $(PNPM) -F @vben/web-tdesign run test:cov

check: test-backend test-frontend ## 测试 + 前端 lint/typecheck 一键回归
	cd frontend && $(PNPM) lint && $(PNPM) check:type
