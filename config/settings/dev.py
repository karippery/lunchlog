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