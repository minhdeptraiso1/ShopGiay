from datetime import timedelta
from decimal import Decimal
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parents[2]
env = environ.Env()
env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY", default="unsafe-base-placeholder")
DEBUG = False
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "apps.accounts",
    "apps.catalog",
    "apps.orders",
    "apps.engagement",
    "apps.exchanges",
    "apps.health",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "common.middleware.RequestIDMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": env.db(
        "DATABASE_URL", default="postgresql://postgres:postgres@127.0.0.1:5432/dijango"
    )
}
if DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql":
    DATABASES["default"].setdefault("OPTIONS", {})["connect_timeout"] = env.int(
        "DATABASE_CONNECT_TIMEOUT", default=3
    )
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL", default="redis://127.0.0.1:6379/1"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": env.int("REDIS_CONNECT_TIMEOUT", default=2),
            "SOCKET_TIMEOUT": env.int("REDIS_SOCKET_TIMEOUT", default=2),
        },
        "KEY_PREFIX": env("REDIS_KEY_PREFIX", default="django_base"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
AUTH_USER_MODEL = "accounts.User"
# Uniqueness is enforced by the case-insensitive Lower(email) database constraint.
SILENCED_SYSTEM_CHECKS = ["auth.E003"]

LANGUAGE_CODE = "vi"
TIME_ZONE = env("DJANGO_TIME_ZONE", default="Asia/Bangkok")
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_HTTPONLY = False

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["apps.accounts.authentication.ActiveUserJWTAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "common.exceptions.api_exception_handler",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "NUM_PROXIES": env.int("DRF_NUM_PROXIES", default=0),
    "DEFAULT_THROTTLE_RATES": {
        "login": env("LOGIN_THROTTLE_RATE", default="5/min"),
        "refresh": env("REFRESH_THROTTLE_RATE", default="10/min"),
        "register": env("REGISTER_THROTTLE_RATE", default="5/hour"),
        "password_reset": env("PASSWORD_RESET_THROTTLE_RATE", default="5/hour"),
        "event": env("EVENT_THROTTLE_RATE", default="120/min"),
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=env.int("JWT_ACCESS_MINUTES", default=5)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env.int("JWT_REFRESH_DAYS", default=7)),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "SIGNING_KEY": env("JWT_SIGNING_KEY", default=SECRET_KEY),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}
REFRESH_TOKEN_COOKIE_NAME = env("REFRESH_TOKEN_COOKIE_NAME", default="refresh_token")
REFRESH_TOKEN_COOKIE_PATH = "/api/v1/auth/"
REFRESH_TOKEN_COOKIE_DOMAIN = env("REFRESH_TOKEN_COOKIE_DOMAIN", default=None) or None
REFRESH_TOKEN_COOKIE_SECURE = env.bool("REFRESH_TOKEN_COOKIE_SECURE", default=True)
REFRESH_TOKEN_COOKIE_SAMESITE = env("REFRESH_TOKEN_COOKIE_SAMESITE", default="Lax")
REFRESH_TOKEN_COOKIE_MAX_AGE = env.int("JWT_REFRESH_DAYS", default=7) * 24 * 60 * 60

SPECTACULAR_SETTINGS = {
    "TITLE": "Django Backend Base API",
    "DESCRIPTION": "API nền tảng dùng lại cho các dự án Django.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "ENUM_NAME_OVERRIDES": {
        "ProductStatusEnum": "apps.catalog.models.Product.Status",
        "ProductEventTypeEnum": "apps.catalog.models.ProductEvent.EventType",
        "ProductEventSourceEnum": "apps.catalog.models.ProductEvent.Source",
        "StockMovementKindEnum": "apps.catalog.models.StockMovement.Kind",
        "OrderStatusEnum": "apps.orders.models.Order.Status",
        "PaymentMethodEnum": "apps.orders.models.Order.PaymentMethod",
        "PaymentStatusEnum": "apps.orders.models.Order.PaymentStatus",
        "PaymentProviderEnum": "apps.orders.models.Payment.Provider",
        "PaymentAttemptStatusEnum": "apps.orders.models.PaymentAttempt.Status",
        "ReservationStatusEnum": "apps.orders.models.InventoryReservation.Status",
        "ExchangeStatusEnum": "apps.exchanges.models.ExchangeRequest.Status",
        "ExchangeDispositionEnum": "apps.exchanges.models.ExchangeItem.Disposition",
        "ExchangeReservationStatusEnum": "apps.exchanges.models.ExchangeReservation.Status",
    },
}
API_DOCS_ENABLED = env.bool("API_DOCS_ENABLED", default=False)
DEMO_USER_EMAIL = env("DEMO_USER_EMAIL", default="demo@example.com")
DEMO_USER_PASSWORD = env("DEMO_USER_PASSWORD", default="123456")
FRONTEND_BASE_URL = env("FRONTEND_BASE_URL", default="http://localhost:5173")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="no-reply@example.com")
EMAIL_HOST = env("EMAIL_HOST", default="localhost")
EMAIL_PORT = env.int("EMAIL_PORT", default=25)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=False)
EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL", default=False)
EMAIL_TIMEOUT = env.int("EMAIL_TIMEOUT", default=10)
EMAIL_BACKEND_SETTING = env("EMAIL_BACKEND", default="auto")
EMAIL_SMTP_CONFIGURED = all((EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD))
if EMAIL_BACKEND_SETTING == "auto":
    EMAIL_BACKEND = (
        "django.core.mail.backends.smtp.EmailBackend"
        if EMAIL_SMTP_CONFIGURED
        else "django.core.mail.backends.console.EmailBackend"
    )
else:
    EMAIL_BACKEND = EMAIL_BACKEND_SETTING
SHIPPING_FLAT_FEE = Decimal(env("SHIPPING_FLAT_FEE", default="30000"))
FREE_SHIPPING_THRESHOLD = Decimal(env("FREE_SHIPPING_THRESHOLD", default="1000000"))
PAYMENT_RESERVATION_MINUTES = env.int("PAYMENT_RESERVATION_MINUTES", default=15)
VNPAY_PAYMENT_URL = env(
    "VNPAY_PAYMENT_URL", default="https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
)
VNPAY_TMN_CODE = env("VNPAY_TMN_CODE", default="")
VNPAY_HASH_SECRET = env("VNPAY_HASH_SECRET", default="")
VNPAY_RETURN_URL = env("VNPAY_RETURN_URL", default="http://localhost:5173/payment/vnpay-return")
VNPAY_VERSION = env("VNPAY_VERSION", default="2.1.0")
VNPAY_COMMAND = env("VNPAY_COMMAND", default="pay")
VNPAY_ORDER_TYPE = env("VNPAY_ORDER_TYPE", default="other")
EXCHANGE_WINDOW_DAYS = env.int("EXCHANGE_WINDOW_DAYS", default=30)
EXCHANGE_RESERVATION_MINUTES = env.int("EXCHANGE_RESERVATION_MINUTES", default=1440)

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = env.bool("USE_X_FORWARDED_HOST", default=False)
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=3600)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = False

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "{asctime} {levelname} {name} request_id={request_id} {message}",
            "style": "{",
        }
    },
    "filters": {"request_id": {"()": "common.middleware.RequestIDLogFilter"}},
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "filters": ["request_id"],
        }
    },
    "root": {"handlers": ["console"], "level": env("LOG_LEVEL", default="INFO")},
}
