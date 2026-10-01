from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.orders.models import PaymentAttempt, PaymentEvent


class Command(BaseCommand):
    help = "Report VNPay attempts that require operational reconciliation."

    def handle(self, *args, **options) -> None:
        pending_expired = PaymentAttempt.objects.filter(
            status=PaymentAttempt.Status.PENDING,
            expires_at__lte=timezone.now(),
        ).count()
        invalid_events = PaymentEvent.objects.filter(signature_valid=False).count()
        unmatched_events = PaymentEvent.objects.filter(
            outcome__in=("received", "invalid_amount")
        ).count()
        self.stdout.write(
            f"pending_expired={pending_expired} invalid_events={invalid_events} "
            f"unmatched_events={unmatched_events}"
        )
