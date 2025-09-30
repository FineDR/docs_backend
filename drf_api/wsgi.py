"""
WSGI config for drf_api project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from dotenv import load_dotenv
import sys

# Project base directory
project_home = '/home/yourusername/docs_backend'
if project_home not in sys.path:
    sys.path.append(project_home)

# Load environment variables
load_dotenv(os.path.join(project_home, ".env.production"))

# Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "drf_api.settings")

application = get_wsgi_application()
