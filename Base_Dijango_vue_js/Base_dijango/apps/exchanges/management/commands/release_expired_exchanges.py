from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.exchanges.models import ExchangeRequest
from apps.exchanges.services import expire_exchange


class Command(BaseCommand):
    help = "Hoàn tồn các biến thể đang giữ cho yêu cầu đổi hàng đã hết hạn."

    def handle(self, *args, **options):
        exchange_ids = list(
            ExchangeRequest.objects.filter(
                status=ExchangeRequest.Status.APPROVED,
                reservation_expires_at__lte=timezone.now(),
            ).values_list("id", flat=True)
        )
        released = sum(expire_exchange(exchange_id=exchange_id) for exchange_id in exchange_ids)
        self.stdout.write(self.style.SUCCESS(f"Đã xử lý {released} yêu cầu đổi hàng hết hạn."))
