"""
Gunicorn configuration file for Social Media API production deployment.
"""

import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 60
max_requests = 1000
max_requests_jitter = 50

# Restart workers after this many requests, with up to 50 requests variation
preload_app = True

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Process naming
proc_name = 'social_media_api'

# Server mechanics
daemon = False
pidfile = '/tmp/gunicorn.pid'
user = None
group = None
tmp_upload_dir = None

# SSL (configure if using HTTPS directly with Gunicorn)
# keyfile = None
# certfile = None
