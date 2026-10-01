from django.urls import path

from .views import (
    CustomerExchangeCancelView,
    CustomerExchangeConfirmReceivedView,
    CustomerExchangeDetailView,
    CustomerExchangeListCreateView,
)

urlpatterns = [
    path("exchanges/", CustomerExchangeListCreateView.as_view(), name="exchange-list-create"),
    path(
        "exchanges/<int:exchange_id>/", CustomerExchangeDetailView.as_view(), name="exchange-detail"
    ),
    path(
        "exchanges/<int:exchange_id>/cancel/",
        CustomerExchangeCancelView.as_view(),
        name="exchange-cancel",
    ),
    path(
        "exchanges/<int:exchange_id>/confirm-received/",
        CustomerExchangeConfirmReceivedView.as_view(),
        name="exchange-confirm-received",
    ),
]
