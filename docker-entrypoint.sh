#!/bin/sh

# Start server
python3 manage.py migrate --noinput
gunicorn -c gunicorn_config.py

nginx -g "daemon off;"
