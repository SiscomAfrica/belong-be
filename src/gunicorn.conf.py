from __future__ import annotations

import multiprocessing

bind = "0.0.0.0:8000"
workers = (2 * multiprocessing.cpu_count()) + 1
worker_class = "gthread"
worker_tmp_dir = "/dev/shm"
threads = 2
timeout = 120
graceful_timeout = 30
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
accesslog = "-"
errorlog = "-"
loglevel = "info"
