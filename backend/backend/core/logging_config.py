"""应用日志：控制台输出全量；文件分「普通」与「错误」两级。"""

from __future__ import annotations

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

_LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
_LOG_DATEFMT = "%Y-%m-%d %H:%M:%S"
_MAX_BYTES = 10 * 1024 * 1024
_BACKUP_COUNT = 5
_FALLBACK_LOG_DIR = "logs"  # 相对于进程 cwd，可通过 LOG_DIR 环境变量覆盖


class _BelowErrorFilter(logging.Filter):
    """只写入普通日志文件：INFO、WARNING（不含 ERROR）。"""

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno < logging.ERROR


def _parse_root_level() -> int:
    name = os.getenv("LOG_LEVEL", "INFO").upper().strip()
    level = getattr(logging, name, None)
    return level if isinstance(level, int) else logging.INFO


def setup_logging() -> None:
    """
    配置根 logger：
    - 控制台：按 LOG_LEVEL（默认 INFO）输出全量级别。
    - app.log：普通业务日志（INFO、WARNING），按大小轮转。
    - error.log：仅 ERROR、CRITICAL，按大小轮转。
    日志目录优先读取 LOG_DIR 环境变量，未设置则默认 ./logs（相对进程启动目录）。
    """
    log_dir = Path(os.getenv("LOG_DIR", _FALLBACK_LOG_DIR))
    log_dir.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(_parse_root_level())

    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_LOG_DATEFMT)

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(root.level)
    console.setFormatter(formatter)
    root.addHandler(console)

    app_path = log_dir / "app.log"
    app_handler = RotatingFileHandler(
        app_path,
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8",
    )
    app_handler.setLevel(logging.INFO)
    app_handler.addFilter(_BelowErrorFilter())
    app_handler.setFormatter(formatter)
    root.addHandler(app_handler)

    err_path = log_dir / "error.log"
    err_handler = RotatingFileHandler(
        err_path,
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8",
    )
    err_handler.setLevel(logging.ERROR)
    err_handler.setFormatter(formatter)
    root.addHandler(err_handler)

    # 降低第三方噪声（仍可在 LOG_LEVEL=DEBUG 时看到）
    logging.getLogger("urllib3").setLevel(logging.WARNING)
