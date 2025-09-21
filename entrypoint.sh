#!/bin/sh
set -e

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn --workers 3 --timeout 120 --bind 0.0.0.0:$PORT drf_api.wsgi:application
