"""
WSGI config for drf_api project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# Set default settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drf_api.settings')

# --- Run migrations programmatically ---
import django
from django.core.management import call_command

django.setup()

try:
    print("Applying database migrations...")
    call_command("migrate", interactive=False)
    print("Migrations applied successfully.")
except Exception as e:
    print(f"Error running migrations: {e}")

# --- Initialize WSGI application ---
application = get_wsgi_application()
