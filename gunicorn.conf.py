# Gunicorn configuration file
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
backlog = 2048

# Worker processes
workers = int(os.getenv('WORKERS', '4'))
worker_class = 'gevent'
worker_connections = 1000
timeout = int(os.getenv('TIMEOUT', '120'))
keepalive = 2

# Restart workers after this many requests, to prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = '/app/logs/gunicorn-access.log'
errorlog = '/app/logs/gunicorn-error.log'
loglevel = os.getenv('LOG_LEVEL', 'info').lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'astro_engine'

# Server mechanics
daemon = False
pidfile = '/tmp/gunicorn.pid'
user = 'astro'
group = 'astro'
tmp_upload_dir = None

# SSL (if needed)
# keyfile = '/path/to/keyfile'
# certfile = '/path/to/certfile'

# Preload application for better performance
preload_app = True

# Enable stats
statsd_host = None
statsd_prefix = 'astro_engine'
