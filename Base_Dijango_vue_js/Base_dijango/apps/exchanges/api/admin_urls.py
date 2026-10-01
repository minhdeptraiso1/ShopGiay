from django.urls import path

from .views import AdminExchangeDetailView, AdminExchangeListView, AdminExchangeTransitionView

urlpatterns = [
    path("exchanges/", AdminExchangeListView.as_view(), name="admin-exchange-list"),
    path(
        "exchanges/<int:exchange_id>/",
        AdminExchangeDetailView.as_view(),
        name="admin-exchange-detail",
    ),
    path(
        "exchanges/<int:exchange_id>/transitions/",
        AdminExchangeTransitionView.as_view(),
        name="admin-exchange-transition",
    ),
]
