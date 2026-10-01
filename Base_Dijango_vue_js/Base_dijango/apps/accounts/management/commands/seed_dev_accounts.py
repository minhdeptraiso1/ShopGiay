from dataclasses import dataclass

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.accounts.roles import BusinessRole


@dataclass(frozen=True)
class DevelopmentAccount:
    email: str
    full_name: str
    role: BusinessRole
    is_staff: bool = False
    is_superuser: bool = False


DEVELOPMENT_ACCOUNTS = (
    DevelopmentAccount("customer@example.com", "Customer Local", BusinessRole.CUSTOMER),
    DevelopmentAccount("staff@example.com", "Staff Local", BusinessRole.STAFF, is_staff=True),
    DevelopmentAccount(
        "admin@example.com",
        "Admin Local",
        BusinessRole.ADMIN,
        is_staff=True,
        is_superuser=True,
    ),
)


class Command(BaseCommand):
    help = "Create or repair the three local CUSTOMER, STAFF and ADMIN test accounts."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--password", default=settings.DEMO_USER_PASSWORD)

    def handle(self, *args, **options) -> None:
        if not settings.DEBUG:
            raise CommandError("seed_dev_accounts is disabled when DEBUG=False")

        user_model = get_user_model()
        password = options["password"]
        with transaction.atomic():
            groups = {
                role: Group.objects.get(name=role)
                for role in (
                    BusinessRole.CUSTOMER,
                    BusinessRole.STAFF,
                    BusinessRole.ADMIN,
                )
            }
            for account in DEVELOPMENT_ACCOUNTS:
                email = user_model.objects.normalize_email_address(account.email)
                user = user_model.objects.filter(email__iexact=email).first()
                if user is None:
                    user = user_model(email=email)
                user.full_name = account.full_name
                user.is_active = True
                user.is_staff = account.is_staff
                user.is_superuser = account.is_superuser
                user.set_password(password)
                user.full_clean(exclude=["password"])
                user.save()
                user.groups.set([groups[account.role]])

        self.stdout.write(self.style.SUCCESS("Three local role accounts are ready."))
