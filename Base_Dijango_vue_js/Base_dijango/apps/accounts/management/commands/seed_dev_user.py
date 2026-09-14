from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create an idempotent local demo user for testing the API."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--email", default=settings.DEMO_USER_EMAIL)
        parser.add_argument("--password", default=settings.DEMO_USER_PASSWORD)
        parser.add_argument(
            "--reset-password",
            action="store_true",
            help="Reset the password if the demo user already exists.",
        )

    def handle(self, *args, **options) -> None:
        if not settings.DEBUG:
            raise CommandError("seed_dev_user is disabled when DEBUG=False")

        user_model = get_user_model()
        email = user_model.objects.normalize_email_address(options["email"])
        password = options["password"]
        user = user_model.objects.filter(email__iexact=email).first()

        if user is None:
            user_model.objects.create_user(
                email=email,
                password=password,
                full_name="Demo User",
                is_active=True,
                is_staff=False,
                is_superuser=False,
            )
            self.stdout.write(self.style.SUCCESS(f"Created demo user: {email}"))
            return

        if not options["reset_password"]:
            self.stdout.write(f"Demo user already exists: {email}; no changes made")
            return

        user.set_password(password)
        user.save(update_fields=["password"])
        self.stdout.write(self.style.SUCCESS(f"Reset password for demo user: {email}"))
