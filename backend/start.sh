#!/usr/bin/env bash
set -o errexit

if [[ -n "${MONGODB_URI:-}" && "${MONGODB_URI}" == mongodb* ]]; then
  echo "MongoDB configured. Running migrations..."
  python manage.py migrate --noinput
  python manage.py bootstrap_admin
else
  echo "MONGODB_URI is not configured yet. Starting API without database bootstrap."
fi

exec gunicorn supportdesk.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120
