from django.urls import path

from .admin_views import AdminAccessView

app_name = "admin_api"

urlpatterns = [path("access/", AdminAccessView.as_view(), name="access")]
