#!/bin/sh
set -e
poetry run python manage.py migrate --noinput
poetry run python manage.py collectstatic --noinput
exec poetry run gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers "${GUNICORN_WORKERS:-2}" \
  --timeout 120
