from logger_extra.extras.gunicorn import JsonErrorFormatter, JsonFormatter

workers = 3  # Number of worker processes
bind = "0.0.0.0:8000"  # Bind Gunicorn to all interfaces on port 8000
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


logconfig_dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "context": {
            "()": "logger_extra.filter.LoggerContextFilter",
        }
    },
    "formatters": {
        "json": {
            "()": JsonFormatter,
        },
        "json_error": {
            "()": JsonErrorFormatter,
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "filters": ["context"],
            "stream": "ext://sys.stdout",
        },
        "error_console": {
            "class": "logging.StreamHandler",
            "formatter": "json_error",
            "filters": ["context"],
            "stream": "ext://sys.stderr",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "gunicorn.access": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "gunicorn.error": {
            "level": "INFO",
            "handlers": ["error_console"],
            "propagate": False,
        },
    },
}
