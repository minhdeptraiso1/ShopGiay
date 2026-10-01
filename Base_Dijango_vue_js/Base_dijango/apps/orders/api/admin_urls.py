from django.urls import path

from .admin_views import AdminOrderDetailView, AdminOrderListView, AdminOrderTransitionView

urlpatterns = [
    path("orders/", AdminOrderListView.as_view(), name="admin-order-list"),
    path("orders/<int:order_id>/", AdminOrderDetailView.as_view(), name="admin-order-detail"),
    path(
        "orders/<int:order_id>/transitions/",
        AdminOrderTransitionView.as_view(),
        name="admin-order-transition",
    ),
]
