import os

os.environ.setdefault("DJANGO_SECRET_KEY", "test-secret-not-for-production")
os.environ.setdefault("JWT_SIGNING_KEY", "test-jwt-secret-not-for-production")
os.environ.setdefault("DATABASE_URL", "postgresql://postgres:postgres@127.0.0.1:5432/dijango")
os.environ.setdefault("REDIS_URL", "redis://127.0.0.1:6379/15")

from .base import *  # noqa: E402,F403
from .base import CACHES, MIDDLEWARE, env  # noqa: E402

DEBUG = False
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]
API_DOCS_ENABLED = True
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
CACHES["default"]["KEY_PREFIX"] = f"django_base_test_{os.getpid()}"
if env.bool("TEST_USE_LOCMEM_CACHE", default=False):
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
MIDDLEWARE = [item for item in MIDDLEWARE if item != "whitenoise.middleware.WhiteNoiseMiddleware"]
