from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.orders.models import InventoryReservation
from apps.orders.payments import expire_order_reservations


class Command(BaseCommand):
    help = "Release expired online-payment inventory reservations idempotently."

    def handle(self, *args, **options) -> None:
        order_ids = list(
            InventoryReservation.objects.filter(
                status=InventoryReservation.Status.ACTIVE,
                expires_at__lte=timezone.now(),
            )
            .values_list("order_item__order_id", flat=True)
            .distinct()
        )
        released = sum(expire_order_reservations(order_id=order_id) for order_id in order_ids)
        self.stdout.write(self.style.SUCCESS(f"Released {released} expired order reservation(s)."))
