from django.urls import path

from .views import (
    CartItemCreateView,
    CartItemDetailView,
    CartView,
    CheckoutQuoteView,
    OrderCancelView,
    OrderConfirmReceivedView,
    OrderDetailView,
    OrderListCreateView,
    OrderPaymentView,
    VnpayIpnView,
    VnpayReturnView,
)

urlpatterns = [
    path("cart/", CartView.as_view(), name="cart"),
    path("cart/items/", CartItemCreateView.as_view(), name="cart-item-create"),
    path("cart/items/<int:item_id>/", CartItemDetailView.as_view(), name="cart-item-detail"),
    path("checkout/quote/", CheckoutQuoteView.as_view(), name="checkout-quote"),
    path("orders/", OrderListCreateView.as_view(), name="order-list-create"),
    path("orders/<int:order_id>/", OrderDetailView.as_view(), name="order-detail"),
    path("orders/<int:order_id>/cancel/", OrderCancelView.as_view(), name="order-cancel"),
    path(
        "orders/<int:order_id>/confirm-received/",
        OrderConfirmReceivedView.as_view(),
        name="order-confirm-received",
    ),
    path("orders/<int:order_id>/payment/", OrderPaymentView.as_view(), name="order-payment"),
    path(
        "orders/<int:order_id>/payment/vnpay-return/",
        VnpayReturnView.as_view(),
        name="vnpay-return",
    ),
    path("payments/vnpay/ipn/", VnpayIpnView.as_view(), name="vnpay-ipn"),
]
