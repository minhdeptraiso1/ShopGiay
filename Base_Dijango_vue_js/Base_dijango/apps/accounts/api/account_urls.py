from django.urls import path

from .address_views import AddressDetailView, AddressListCreateView, SetDefaultAddressView

app_name = "account_api"

urlpatterns = [
    path("addresses/", AddressListCreateView.as_view(), name="address-list"),
    path("addresses/<int:address_id>/", AddressDetailView.as_view(), name="address-detail"),
    path(
        "addresses/<int:address_id>/set-default/",
        SetDefaultAddressView.as_view(),
        name="address-set-default",
    ),
]
