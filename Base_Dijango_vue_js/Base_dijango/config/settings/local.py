from .base import *  # noqa: F403
from .base import env

SECRET_KEY = env("DJANGO_SECRET_KEY", default="local-only-insecure-secret-change-me")
DEBUG = env.bool("DJANGO_DEBUG", default=True)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
DATABASES = {
    "default": env.db(
        "DATABASE_URL", default="postgresql://postgres:postgres@127.0.0.1:5432/dijango"
    )
}
CACHES["default"]["LOCATION"] = env(  # noqa: F405
    "REDIS_URL", default="redis://127.0.0.1:6379/1"
)
SIMPLE_JWT["SIGNING_KEY"] = env("JWT_SIGNING_KEY", default=SECRET_KEY)  # noqa: F405
API_DOCS_ENABLED = env.bool("API_DOCS_ENABLED", default=True)
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
REFRESH_TOKEN_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
