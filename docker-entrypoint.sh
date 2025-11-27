#!/bin/bash

set -e

if [ -z "$SKIP_DATABASE_CHECK" ] || [ "$SKIP_DATABASE_CHECK" = "0" ]; then
    until nc --verbose --wait 30 -z "$DATABASE_HOST" 5432
    do
      echo "Waiting for postgres database connection..."
      sleep 1
    done
    echo "Database is up!"
fi

# Apply database migrations
if [[ "$APPLY_MIGRATIONS" = "1" ]]; then
    echo "Applying database migrations..."
    ./manage.py migrate --noinput
fi

# Start server
if [[ -n "$*" ]]; then
    "$@"
elif [[ "$DEV_SERVER" = "1" ]]; then
    python -Wd ./manage.py runserver 0.0.0.0:8080
else
  gunicorn &
  nginx -g "daemon off;"
fi
