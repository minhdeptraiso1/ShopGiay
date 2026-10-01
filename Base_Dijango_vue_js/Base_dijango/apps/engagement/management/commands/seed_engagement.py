from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.engagement.models import Banner, Voucher


class Command(BaseCommand):
    help = "Tạo voucher và banner demo idempotent cho môi trường phát triển."

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("seed_engagement is disabled when DEBUG=False")

        now = timezone.now()
        voucher, voucher_created = Voucher.objects.update_or_create(
            code="WELCOME10",
            defaults={
                "name": "Ưu đãi khách hàng mới",
                "discount_type": Voucher.DiscountType.PERCENT,
                "value": 10,
                "max_discount": 200_000,
                "min_order_value": 500_000,
                "starts_at": now - timedelta(days=1),
                "ends_at": now + timedelta(days=90),
                "usage_limit": 500,
                "per_user_limit": 1,
                "is_active": True,
            },
        )
        voucher.products.clear()
        voucher.categories.clear()

        banner, banner_created = Banner.objects.update_or_create(
            title="Bộ sưu tập chạy bộ mới",
            position=Banner.Position.HOME_STRIP,
            defaults={
                "subtitle": "Khám phá các mẫu giày hiệu năng cao đang có sẵn tại Hải Duy Shop.",
                "image_url": (
                    "https://images.unsplash.com/photo-1542291026-7eec264c27ff"
                    "?auto=format&fit=crop&w=1600&q=85"
                ),
                "target_url": "/products?category=running",
                "starts_at": now - timedelta(days=1),
                "ends_at": now + timedelta(days=90),
                "sort_order": 10,
                "is_active": True,
            },
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Engagement ready: voucher WELCOME10 "
                f"({'created' if voucher_created else 'updated'}), banner "
                f"({'created' if banner_created else 'updated'})."
            )
        )
