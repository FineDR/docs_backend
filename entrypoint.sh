#!/bin/bash
set -e

# Run migrations
echo "✅ Applying migrations..."
python manage.py migrate --noinput

# Collect static files
echo "✅ Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if needed
echo "✅ Creating superuser..."
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); \
if not User.objects.filter(email='admin@gmail.com').exists(): \
    User.objects.create_superuser(email='admin@gmail.com', password='admin12345', first_name='Super', last_name='Admin', middle_name='System', is_active=True)"

# Start Gunicorn
echo "🚀 Starting Gunicorn..."
exec gunicorn drf_api.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 4 \
    --log-level info \
    --access-logfile '-' \
    --error-logfile '-'
