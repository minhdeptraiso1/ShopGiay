from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("apps.accounts.api.urls")),
    path("api/v1/account/", include("apps.accounts.api.account_urls")),
    path("api/v1/admin/", include("apps.accounts.api.admin_urls")),
    path("api/v1/admin/", include("apps.catalog.api.admin_urls")),
    path("api/v1/admin/", include("apps.orders.api.admin_urls")),
    path("api/v1/admin/", include("apps.engagement.api.admin_urls")),
    path("api/v1/admin/", include("apps.exchanges.api.admin_urls")),
    path("api/v1/", include("apps.catalog.api.urls")),
    path("api/v1/", include("apps.orders.api.urls")),
    path("api/v1/", include("apps.engagement.api.urls")),
    path("api/v1/", include("apps.exchanges.api.urls")),
    path("health/", include("apps.health.urls")),
]

if settings.API_DOCS_ENABLED:
    urlpatterns += [
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
        path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
