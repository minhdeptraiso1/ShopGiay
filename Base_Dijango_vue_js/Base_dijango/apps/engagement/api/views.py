from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdmin, IsCustomer, IsStaffOrAdmin
from apps.catalog.models import Product
from apps.orders.services import build_checkout_quote

from ..models import Banner, Review, Voucher
from ..selectors import list_active_banners, list_admin_reviews, list_public_reviews, list_wishlist
from ..services import (
    ReviewEligibilityError,
    VoucherValidationError,
    create_review,
    moderate_review,
    remove_wishlist_item,
    save_banner,
    save_voucher,
    toggle_wishlist,
    update_own_review,
)
from .serializers import (
    BannerSerializer,
    EligibleVoucherOutputSerializer,
    ReviewCreateInputSerializer,
    ReviewModerateInputSerializer,
    ReviewSerializer,
    ReviewUpdateInputSerializer,
    VoucherAdminSerializer,
    VoucherValidateInputSerializer,
    VoucherValidationOutputSerializer,
    WishlistItemSerializer,
    WishlistToggleInputSerializer,
    WishlistToggleOutputSerializer,
)


class BannerPublicListView(ListAPIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    serializer_class = BannerSerializer
    pagination_class = None

    def get_queryset(self):
        return list_active_banners(position=self.request.query_params.get("position", ""))


class VoucherValidateView(APIView):
    permission_classes = [IsCustomer]

    @extend_schema(
        tags=["Engagement"],
        request=VoucherValidateInputSerializer,
        responses={200: VoucherValidationOutputSerializer},
    )
    def post(self, request):
        serializer = VoucherValidateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            quote = build_checkout_quote(user=request.user, **serializer.validated_data)
        except VoucherValidationError as exc:
            raise serializers.ValidationError({"code": str(exc)}) from exc
        return Response(
            VoucherValidationOutputSerializer(
                {
                    "code": quote.voucher_code,
                    "discount_total": quote.discount_total,
                    "subtotal": quote.subtotal,
                    "total": quote.total,
                    "currency": quote.currency,
                }
            ).data
        )


class EligibleVoucherListView(APIView):
    permission_classes = [IsCustomer]

    @extend_schema(
        tags=["Engagement"],
        request=VoucherValidateInputSerializer,
        responses={200: EligibleVoucherOutputSerializer},
    )
    def post(self, request):
        serializer = VoucherValidateInputSerializer(data={"code": "ELIGIBLE", **request.data})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        points_balance = getattr(getattr(request.user, "loyalty_account", None), "balance", 0)
        candidates = Voucher.objects.filter(
            is_active=True,
            starts_at__lte=timezone.now(),
            ends_at__gt=timezone.now(),
            required_points__lte=points_balance,
        ).order_by("required_points", "code")
        vouchers = []
        for voucher in candidates:
            try:
                quote = build_checkout_quote(
                    user=request.user,
                    address_id=data["address_id"],
                    cart_item_ids=data["cart_item_ids"],
                    voucher_code=voucher.code,
                )
            except VoucherValidationError:
                continue
            vouchers.append(
                {
                    "id": voucher.id,
                    "code": voucher.code,
                    "name": voucher.name,
                    "discount_type": voucher.discount_type,
                    "value": voucher.value,
                    "max_discount": voucher.max_discount,
                    "min_order_value": voucher.min_order_value,
                    "required_points": voucher.required_points,
                    "discount_total": quote.discount_total,
                    "total": quote.total,
                }
            )
        return Response({"points_balance": points_balance, "vouchers": vouchers})


class WishlistView(APIView):
    permission_classes = [IsCustomer]

    @extend_schema(tags=["Engagement"], responses={200: WishlistItemSerializer(many=True)})
    def get(self, request):
        items = list_wishlist(user_id=request.user.id)
        return Response(WishlistItemSerializer(items, many=True, context={"request": request}).data)

    @extend_schema(
        tags=["Engagement"],
        request=WishlistToggleInputSerializer,
        responses={200: WishlistToggleOutputSerializer},
    )
    def post(self, request):
        serializer = WishlistToggleInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data["product"]
        _, active = toggle_wishlist(user=request.user, product=product)
        return Response({"product_id": product.id, "is_wishlisted": active})


class WishlistDetailView(APIView):
    permission_classes = [IsCustomer]

    @extend_schema(tags=["Engagement"], responses={204: None})
    def delete(self, request, product_id: int):
        remove_wishlist_item(user=request.user, product_id=product_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductReviewListCreateView(APIView):
    def get_permissions(self):
        return [permissions.AllowAny()] if self.request.method == "GET" else [IsCustomer()]

    @extend_schema(tags=["Engagement"], responses={200: ReviewSerializer(many=True)})
    def get(self, request, product_id: int):
        reviews = list_public_reviews(product_id=product_id)
        return Response(ReviewSerializer(reviews, many=True).data)

    @extend_schema(
        tags=["Engagement"],
        request=ReviewCreateInputSerializer,
        responses={201: ReviewSerializer},
    )
    def post(self, request, product_id: int):
        product = get_object_or_404(Product, pk=product_id, status=Product.Status.PUBLISHED)
        serializer = ReviewCreateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            review = create_review(
                user=request.user,
                product=product,
                order_item_id=serializer.validated_data.pop("order_item"),
                **serializer.validated_data,
            )
        except ReviewEligibilityError as exc:
            raise serializers.ValidationError({"order_item": str(exc)}) from exc
        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)


class OwnReviewDetailView(APIView):
    permission_classes = [IsCustomer]

    @extend_schema(
        tags=["Engagement"],
        request=ReviewUpdateInputSerializer,
        responses={200: ReviewSerializer},
    )
    def patch(self, request, review_id: int):
        review = get_object_or_404(Review, pk=review_id, user=request.user)
        serializer = ReviewUpdateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review = update_own_review(review=review, **serializer.validated_data)
        return Response(ReviewSerializer(review).data)

    @extend_schema(tags=["Engagement"], responses={204: None})
    def delete(self, request, review_id: int):
        review = get_object_or_404(Review, pk=review_id, user=request.user)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VoucherAdminViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = VoucherAdminSerializer
    queryset = Voucher.objects.prefetch_related("products", "categories").annotate(
        usage_count=Count("usages", filter=Q(usages__status__in=("reserved", "redeemed")))
    )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        voucher = save_voucher(instance=None, data=dict(serializer.validated_data))
        return Response(self.get_serializer(voucher).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        voucher = self.get_object()
        serializer = self.get_serializer(
            voucher, data=request.data, partial=kwargs.get("partial", False)
        )
        serializer.is_valid(raise_exception=True)
        voucher = save_voucher(instance=voucher, data=dict(serializer.validated_data))
        return Response(self.get_serializer(voucher).data)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=["is_active", "updated_at"])


class BannerAdminViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = BannerSerializer
    queryset = Banner.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        banner = save_banner(instance=None, data=dict(serializer.validated_data))
        return Response(self.get_serializer(banner).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        banner = self.get_object()
        serializer = self.get_serializer(
            banner, data=request.data, partial=kwargs.get("partial", False)
        )
        serializer.is_valid(raise_exception=True)
        banner = save_banner(instance=banner, data=dict(serializer.validated_data))
        return Response(self.get_serializer(banner).data)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=["is_active", "updated_at"])


class AdminReviewListView(ListAPIView):
    permission_classes = [IsStaffOrAdmin]
    serializer_class = ReviewSerializer

    def get_queryset(self):
        queryset = list_admin_reviews()
        review_status = self.request.query_params.get("status")
        return queryset.filter(status=review_status) if review_status else queryset


class AdminReviewModerateView(APIView):
    permission_classes = [IsStaffOrAdmin]

    @extend_schema(
        tags=["Admin engagement"],
        request=ReviewModerateInputSerializer,
        responses={200: ReviewSerializer},
    )
    @transaction.atomic
    def post(self, request, review_id: int):
        serializer = ReviewModerateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review = get_object_or_404(Review.objects.select_for_update(), pk=review_id)
        review = moderate_review(
            review=review,
            moderator=request.user,
            status=serializer.validated_data["status"],
            note=serializer.validated_data.get("moderation_note", ""),
        )
        return Response(ReviewSerializer(review).data)
