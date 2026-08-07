"""
Enterprise-grade Gunicorn configuration optimized for Django production workloads.
"""
import multiprocessing
import os
import tempfile
import sys

# ------------------------------------------------------------------------------
# Binding & Network
# ------------------------------------------------------------------------------
bind = "0.0.0.0:8000"

# ------------------------------------------------------------------------------
# Process & Thread Tuning
# ------------------------------------------------------------------------------
# Automatically calculate optimal workers based on available CPU cores.
# Formula: (2 * CPU Cores) + 1
try:
    cpu_cores = multiprocessing.cpu_count()
except Exception:
    cpu_cores = 1

workers = (2 * cpu_cores) + 1

# Thread-based concurrency per worker
threads = 2
worker_class = "gthread"

# ------------------------------------------------------------------------------
# Timeouts & Keepalive
# ------------------------------------------------------------------------------
timeout = 120
graceful_timeout = 30
keepalive = 5

# ------------------------------------------------------------------------------
# Request Recycling (Memory Leak Prevention)
# ------------------------------------------------------------------------------
# Restart workers periodically to prevent memory leaks in Python
max_requests = 1000
# Add jitter to prevent all workers from restarting simultaneously
max_requests_jitter = 100

# ------------------------------------------------------------------------------
# Process Naming & Security
# ------------------------------------------------------------------------------
proc_name = "grantloop-backend"
# Docker containers already execute as a restricted user (see Dockerfile).
# Do not attempt to drop privileges here.
user = None
group = None

# ------------------------------------------------------------------------------
# Performance & Shared Memory
# ------------------------------------------------------------------------------
# Load application code before the worker processes are forked.
# Speeds up boot times and shares memory across workers.
preload_app = True

# Use RAM-backed file system for worker temporary files to avoid disk I/O bottlenecks.
# Fallback to OS temp directory if /dev/shm is unavailable (e.g., local Windows dev).
if os.path.exists("/dev/shm"):
    worker_tmp_dir = "/dev/shm"
else:
    worker_tmp_dir = tempfile.gettempdir()

# ------------------------------------------------------------------------------
# Request Limits (Security Defaults against Denial of Service)
# ------------------------------------------------------------------------------
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# ------------------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------------------
log_dir = os.path.join(os.path.dirname(__file__), "logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)

accesslog = os.path.join(log_dir, "gunicorn_access.log")
errorlog = os.path.join(log_dir, "gunicorn_error.log")
capture_output = True

# ------------------------------------------------------------------------------
# Lifecycle Hooks
# ------------------------------------------------------------------------------
def on_starting(server):
    server.log.info("Gunicorn starting: Initializing master process...")

def when_ready(server):
    server.log.info(f"Gunicorn ready: Listening on {bind} with {workers} workers and {threads} threads per worker.")

def worker_int(worker):
    worker.log.info(f"Worker {worker.pid} received INT or QUIT signal. Graceful shutdown initiated.")

def worker_abort(worker):
    worker.log.info(f"Worker {worker.pid} timed out. Aborting forcefully.")

def child_exit(server, worker):
    server.log.info(f"Worker {worker.pid} exited normally.")

# ------------------------------------------------------------------------------
# Diagnostic Helper
# ------------------------------------------------------------------------------
def print_configuration():
    print("=== Gunicorn Production Configuration ===")
    print(f"Workers:          {workers} (Formula: 2 * {cpu_cores} cores + 1)")
    print(f"Threads:          {threads}")
    print(f"Worker Class:     {worker_class}")
    print(f"Bind:             {bind}")
    print(f"Timeout:          {timeout}s")
    print(f"Keepalive:        {keepalive}s")
    print(f"Max Requests:     {max_requests} (Jitter: {max_requests_jitter})")
    print(f"Temp Dir:         {worker_tmp_dir}")
    print("=======================================")

if __name__ == "__main__":
    print_configuration()
