import multiprocessing

# 绑定地址
bind = "127.0.0.1:8001"

# Worker 配置：使用 uvicorn 的 ASGI worker
worker_class = "uvicorn.workers.UvicornWorker"
workers = 4

# 进程管理
daemon = True
pidfile = "/var/run/car-sales/gunicorn.pid"

# 日志
accesslog = "/var/log/car-sales/access.log"
errorlog = "/var/log/car-sales/error.log"
loglevel = "info"

# 优雅重启：等待旧 worker 处理完当前请求再退出
graceful_timeout = 30
timeout = 60

# 预加载应用（节省内存，利用 copy-on-write）
preload_app = True
