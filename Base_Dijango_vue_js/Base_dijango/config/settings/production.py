import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403
from .base import ALLOWED_HOSTS, CORS_ALLOWED_ORIGINS, CSRF_TRUSTED_ORIGINS

required_variables = (
    "DJANGO_SECRET_KEY",
    "JWT_SIGNING_KEY",
    "DATABASE_URL",
    "REDIS_URL",
    "DJANGO_ALLOWED_HOSTS",
    "CORS_ALLOWED_ORIGINS",
    "CSRF_TRUSTED_ORIGINS",
)
missing_variables = [name for name in required_variables if not os.environ.get(name)]
if missing_variables:
    raise ImproperlyConfigured(
        f"Missing required production settings: {', '.join(missing_variables)}"
    )
if not ALLOWED_HOSTS or not CORS_ALLOWED_ORIGINS or not CSRF_TRUSTED_ORIGINS:
    raise ImproperlyConfigured("Production hosts, CORS origins and CSRF origins cannot be empty")
