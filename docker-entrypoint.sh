#!/bin/bash

# Start server
python ./manage.py migrate --noinput
gunicorn pysakoinnin_sahk_asiointi.wsgi:application --bind 0.0.0.0:8000 --daemon

su -c 'nginx -g "daemon off;"'