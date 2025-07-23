from .base import *
import os

# Environment
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]  # More secure than "*"

# Development apps
INSTALLED_APPS += [
    "debug_toolbar",
    "drf_yasg",
    "django_extensions",
]

# Middleware
MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")

# Debug Toolbar
INTERNAL_IPS = ["127.0.0.1"]
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: DEBUG,
    "DISABLE_PANELS": {
        "debug_toolbar.panels.redirects.RedirectsPanel",
    },
    "SHOW_TEMPLATE_CONTEXT": True,
}


# API Documentation
SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header"
        }
    },
    "DEEP_LINKING": True,
    "PERSIST_AUTH": True,
    "REFETCH_SCHEMA_WITH_AUTH": True,
    "USE_SESSION_AUTH": False,
}


# Security settings for development
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
    CSRF_TRUSTED_ORIGINS = ["http://localhost:8000", "http://127.0.0.1:8000"]
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

# Email configuration
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Database configuration for development
DATABASES["default"]["ATOMIC_REQUESTS"] = False

# Enable docs only in development
DOCS_ENABLED = True

# MinIO file storage for user-uploaded media in future switch to AWS S3
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL")
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", default="us-east-1")
AWS_S3_FILE_OVERWRITE = False
AWS_S3_VERIFY = False
AWS_S3_ADDRESSING_STYLE = "path"

# Optional: customize media URL
MEDIA_URL = f"{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/"