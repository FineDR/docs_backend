#!/bin/sh

# --- Run migrations ---
echo "Running migrations..."
python manage.py migrate

# --- Start Gunicorn ---
echo "Starting Gunicorn..."
exec gunicorn --workers 3 --timeout 120 --bind 0.0.0.0:$PORT drf_api.wsgi:application
