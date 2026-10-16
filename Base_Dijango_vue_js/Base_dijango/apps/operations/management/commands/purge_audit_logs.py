from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.operations.models import AuditLog


class Command(BaseCommand):
    help = "Delete audit logs older than the configured retention period."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options) -> None:
        cutoff = timezone.now() - timedelta(days=settings.AUDIT_LOG_RETENTION_DAYS)
        queryset = AuditLog.objects.filter(created_at__lt=cutoff)
        count = queryset.count()
        if not options["dry_run"]:
            queryset.delete()
        mode = "would delete" if options["dry_run"] else "deleted"
        self.stdout.write(f"{mode} {count} audit log(s) older than {cutoff.isoformat()}")
