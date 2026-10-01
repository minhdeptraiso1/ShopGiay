from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Lower

from .managers import UserManager


class User(AbstractUser):
    username = None
    first_name = None
    last_name = None
    email = models.EmailField(max_length=254)
    full_name = models.CharField(max_length=255, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    objects = UserManager()

    class Meta:
        ordering = ("id",)
        constraints = [
            models.UniqueConstraint(Lower("email"), name="accounts_user_email_ci_unique")
        ]

    def save(self, *args, **kwargs) -> None:
        self.email = UserManager.normalize_email_address(self.email)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.email


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    recipient_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    province = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    ward = models.CharField(max_length=100)
    street_address = models.CharField(max_length=255)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-is_default", "-updated_at", "id")
        constraints = [
            models.UniqueConstraint(
                fields=("user",),
                condition=models.Q(is_default=True),
                name="accounts_address_one_default_per_user",
            )
        ]
        indexes = [
            models.Index(fields=("user", "-updated_at"), name="accounts_address_user_updated")
        ]

    def __str__(self) -> str:
        return f"{self.recipient_name} - {self.street_address}"


class LoyaltyAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="loyalty_account")
    balance = models.PositiveBigIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.user.email}: {self.balance} điểm"


class LoyaltyTransaction(models.Model):
    class Kind(models.TextChoices):
        ORDER_REWARD = "order_reward", "Thưởng đơn hàng"
        ADJUSTMENT = "adjustment", "Điều chỉnh"

    account = models.ForeignKey(
        LoyaltyAccount, on_delete=models.PROTECT, related_name="transactions"
    )
    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.PROTECT,
        related_name="loyalty_reward",
        null=True,
        blank=True,
    )
    kind = models.CharField(max_length=24, choices=Kind.choices)
    points = models.BigIntegerField()
    balance_after = models.PositiveBigIntegerField()
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at", "-id")

    def __str__(self) -> str:
        return f"{self.account.user.email}: {self.points:+d}"
