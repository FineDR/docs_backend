"""
Django settings for drf_api project.
Configured for both development and production environments.
"""

from pathlib import Path
import os
import environ
from dotenv import load_dotenv

# --- BASE DIRECTORY ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- LOAD .ENV ---
load_dotenv(os.path.join(BASE_DIR, ".env"))
env = environ.Env(DJANGO_DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# --- SECURITY ---
SECRET_KEY = env("DJANGO_SECRET_KEY", default="django-insecure-default-key")
DEBUG = env.bool("DJANGO_DEBUG", default=True)

# --- HOSTS ---
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["*"])  # no https://

# --- CORS & CSRF ---
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = env.list(
    "DJANGO_CORS_ALLOWED_ORIGINS",
    default=[
        "http://localhost:5173",
        "https://fastdocplatform.netlify.app",
    ]
)
CSRF_TRUSTED_ORIGINS = env.list(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    default=[
        "http://localhost:5173",
        "https://fastdocplatform.netlify.app",
    ]
)

CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG

# --- INSTALLED APPS ---
INSTALLED_APPS = [
    "grappelli",
    "grappelli.dashboard",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework_simplejwt.token_blacklist",

    # Local apps
    "api",
    "smsparser",
    "personal_details",
    "work_experiences",
    "career_objective",
    "skills_app",
    "education_app",
    "language_app",
    "project_app",
    "certificate_app",
    "references_app",
    "achivements_app",
    "cv_payments",
    "jobs",
    "letterApp",

    # Third-party apps
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "drf_yasg",
    "drf_spectacular",
]

# --- MIDDLEWARE ---
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # must be first
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "drf_api.urls"
WSGI_APPLICATION = "drf_api.wsgi.application"

# --- DATABASE ---
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default="postgres://postgres:password@localhost:5432/doc_db"
    )
}

# --- AUTHENTICATION ---
AUTH_USER_MODEL = "api.UserTB"

# --- EMAIL ---
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# --- STRIPE & OPENROUTER ---
STRIPE_TEST_API_KEY = env("STRIPE_TEST_API_KEY", default="")
STRIPE_TEST_SECRET_KEY = env("STRIPE_TEST_SECRET_KEY", default="")
OPENROUTER_API_KEY = env("OPENROUTER_API_KEY", default="")

# --- REST FRAMEWORK ---
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
    ),
}

# --- DRF SPECTACULAR ---
SPECTACULAR_SETTINGS = {
    "TITLE": "It Is Possible API",
    "DESCRIPTION": "Comprehensive API documentation for It Is Possible.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX_TRIM": True,
}

# --- TEMPLATES ---
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# --- GRAPPELLI ---
GRAPPELLI_INDEX_DASHBOARD = "api.dashboard.CustomIndexDashboard"
GRAPPELLI_ADMIN_TITLE = "It Is Possible Admin Dashboard"
FRONTEND_BASE_URL = env("FRONTEND_BASE_URL", default="http://localhost:5173")

# --- PASSWORD VALIDATORS ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- INTERNATIONALIZATION ---
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --- STATIC & MEDIA ---
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# --- DEFAULT PRIMARY KEY ---
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
