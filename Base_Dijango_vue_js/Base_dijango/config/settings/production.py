import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403
from .base import (
    ALLOWED_HOSTS,
    CORS_ALLOWED_ORIGINS,
    CSRF_TRUSTED_ORIGINS,
    EMAIL_BACKEND,
    EMAIL_SMTP_CONFIGURED,
)

required_variables = (
    "DJANGO_SECRET_KEY",
    "JWT_SIGNING_KEY",
    "DATABASE_URL",
    "REDIS_URL",
    "DJANGO_ALLOWED_HOSTS",
    "CORS_ALLOWED_ORIGINS",
    "CSRF_TRUSTED_ORIGINS",
    "FRONTEND_BASE_URL",
    "DEFAULT_FROM_EMAIL",
    "EMAIL_BACKEND",
)
missing_variables = [name for name in required_variables if not os.environ.get(name)]
if missing_variables:
    raise ImproperlyConfigured(
        f"Missing required production settings: {', '.join(missing_variables)}"
    )
if not ALLOWED_HOSTS or not CORS_ALLOWED_ORIGINS or not CSRF_TRUSTED_ORIGINS:
    raise ImproperlyConfigured("Production hosts, CORS origins and CSRF origins cannot be empty")
if EMAIL_BACKEND == "django.core.mail.backends.console.EmailBackend":
    raise ImproperlyConfigured("Production email cannot use the console backend")
if EMAIL_BACKEND == "django.core.mail.backends.smtp.EmailBackend" and not EMAIL_SMTP_CONFIGURED:
    raise ImproperlyConfigured(
        "EMAIL_HOST, EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are required for production SMTP"
    )
