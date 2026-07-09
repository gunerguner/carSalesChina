import multiprocessing
import os

bind = "0.0.0.0:8001"

worker_class = "uvicorn.workers.UvicornWorker"
_default_workers = min(max(2, multiprocessing.cpu_count()), 4)
workers = int(os.getenv("GUNICORN_WORKERS", str(_default_workers)))

daemon = False
pidfile = None

accesslog = "-"
errorlog = "-"
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")

graceful_timeout = 30
timeout = int(os.getenv("GUNICORN_TIMEOUT", "300"))
preload_app = True
