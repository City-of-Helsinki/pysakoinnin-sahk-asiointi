#!/bin/sh

# Start server
python manage.py migrate --noinput
gunicorn pysakoinnin_sahk_asiointi.wsgi:application --bind 0.0.0.0:8000 --daemon --capture-output --enable-stdio-inheritance

nginx -g "daemon off;"