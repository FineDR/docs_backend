#!/bin/bash
# entrypoint.sh

# Exit on errors
set -e

# Apply migrations
echo "Applying database migrations..."
python manage.py migrate

# Create superuser if needed
python manage.py shell -c "from api.views import run_create_superuser; from django.http import HttpRequest; run_create_superuser(HttpRequest())"

# Start Celery worker in background
echo "Starting Celery worker..."
celery -A drf_api worker --loglevel=info &

# Start Gunicorn server
echo "Starting Gunicorn server..."
exec gunicorn drf_api.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 3 \
    --threads 4 \
    --worker-class gthread
