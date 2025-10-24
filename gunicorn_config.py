workers = 3  # Number of worker processes
threads = 1  # Enable threads per worker (similar to enable-threads in uWSGI)
worker_class = "sync"  # Or use "gthread" for explicit threading support
bind = "0.0.0.0:8000"  # Bind Gunicorn to all interfaces on port 8000
daemon = True  # Run Gunicorn in the background
wsgi_app = "pysakoinnin_sahk_asiointi.wsgi:application"  # WSGI application entry point
accesslog = "-"  # Log access to stdout
errorlog = "-"  # Log errors to stderr
limit_request_field_size = 65536  # Limit request header size
capture_output = True  # Capture stdout/stderr in logs
timeout = 30  # Timeout for requests in seconds
graceful_timeout = 30  # Timeout for graceful shutdown
keepalive = 2  # Keep-alive time for connections in seconds
enable_stdio_inheritance = True  # Inherit stdio from the parent process
# Worker Restart Settings
max_requests = 1000  # Restart workers after processing 1000 requests
max_requests_jitter = 50  # Add randomness to avoid mass restarts
