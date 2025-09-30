"""
WSGI config for drf_api project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
import sys
from django.core.wsgi import get_wsgi_application
from dotenv import load_dotenv

# --- Project base directory ---
project_home = '/home/kululinda/docs_backend'  # Change to your PythonAnywhere path if needed
if project_home not in sys.path:
    sys.path.append(project_home)

# --- Load environment variables ---
# Use the .env file you have locally or create a .env.production for production
load_dotenv(os.path.join(project_home, ".env"))  # or ".env.production" if you prefer

# --- Set Django settings module ---
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "drf_api.settings")

# --- Initialize WSGI application ---
application = get_wsgi_application()
