from django.contrib.auth import get_user_model
from django.db.models import QuerySet

from .models import Address

User = get_user_model()


def get_active_user_by_id(*, user_id: int) -> User | None:
    return User.objects.filter(id=user_id, is_active=True).first()


def list_user_addresses(*, user: User) -> QuerySet[Address]:
    return Address.objects.filter(user=user).order_by("-is_default", "-updated_at", "id")


def get_user_address(*, user: User, address_id: int) -> Address | None:
    return Address.objects.filter(user=user, id=address_id).first()
