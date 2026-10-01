from decimal import ROUND_HALF_UP, Decimal
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from .models import Address, LoyaltyAccount, LoyaltyTransaction
from .roles import BusinessRole

User = get_user_model()


class DuplicateEmailError(Exception):
    pass


class InvalidPasswordResetTokenError(Exception):
    pass


@transaction.atomic
def register_customer(*, email: str, password: str, full_name: str) -> User:
    normalized_email = User.objects.normalize_email_address(email)
    try:
        user = User.objects.create_user(
            email=normalized_email,
            password=password,
            full_name=full_name.strip(),
        )
    except (IntegrityError, DjangoValidationError) as exc:
        if User.objects.filter(email=normalized_email).exists():
            raise DuplicateEmailError from exc
        raise
    customer_group = Group.objects.get(name=BusinessRole.CUSTOMER)
    user.groups.add(customer_group)
    return user


@transaction.atomic
def update_profile(*, user: User, full_name: str) -> User:
    user.full_name = full_name.strip()
    user.full_clean(exclude=["password"])
    user.save(update_fields=["full_name"])
    return user


def request_password_reset(*, email: str) -> None:
    normalized_email = User.objects.normalize_email_address(email)
    user = User.objects.filter(email=normalized_email, is_active=True).first()
    if user is None:
        return

    query = urlencode(
        {
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": default_token_generator.make_token(user),
        }
    )
    reset_url = f"{settings.FRONTEND_BASE_URL.rstrip('/')}/reset-password?{query}"
    send_mail(
        subject="Đặt lại mật khẩu Shoe Store",
        message=(
            "Bạn đã yêu cầu đặt lại mật khẩu. Mở liên kết sau để tiếp tục:\n\n"
            f"{reset_url}\n\n"
            "Nếu bạn không gửi yêu cầu này, hãy bỏ qua email."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


@transaction.atomic
def confirm_password_reset(*, uid: str, token: str, new_password: str) -> User:
    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.select_for_update().get(pk=user_id, is_active=True)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as exc:
        raise InvalidPasswordResetTokenError from exc
    if not default_token_generator.check_token(user, token):
        raise InvalidPasswordResetTokenError
    user.set_password(new_password)
    user.save(update_fields=["password"])
    return user


def _lock_address_owner(user: User) -> User:
    return User.objects.select_for_update().get(pk=user.pk)


@transaction.atomic
def create_address(*, user: User, **address_data: str) -> Address:
    locked_user = _lock_address_owner(user)
    has_addresses = Address.objects.filter(user=locked_user).exists()
    address = Address(user=locked_user, is_default=not has_addresses, **address_data)
    address.full_clean()
    address.save()
    return address


@transaction.atomic
def update_address(*, address: Address, **address_data: str) -> Address:
    _lock_address_owner(address.user)
    locked_address = Address.objects.select_for_update().get(pk=address.pk, user=address.user)
    for field, value in address_data.items():
        setattr(locked_address, field, value)
    locked_address.full_clean()
    locked_address.save(update_fields=(*address_data.keys(), "updated_at"))
    return locked_address


@transaction.atomic
def set_default_address(*, address: Address) -> Address:
    _lock_address_owner(address.user)
    Address.objects.filter(user=address.user, is_default=True).exclude(pk=address.pk).update(
        is_default=False
    )
    address.is_default = True
    address.save(update_fields=["is_default", "updated_at"])
    return address


@transaction.atomic
def delete_address(*, address: Address) -> None:
    _lock_address_owner(address.user)
    was_default = address.is_default
    user = address.user
    address.delete()
    if was_default:
        replacement = Address.objects.filter(user=user).order_by("-updated_at", "id").first()
        if replacement is not None:
            replacement.is_default = True
            replacement.save(update_fields=["is_default", "updated_at"])


@transaction.atomic
def award_order_loyalty_points(*, order) -> int:
    """Award 0.5% of the paid order value once, rounded to the nearest point."""
    if LoyaltyTransaction.objects.filter(order=order).exists():
        return 0
    points = int(
        (Decimal(order.total) * Decimal("0.005")).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    )
    if points <= 0:
        return 0
    account, _ = LoyaltyAccount.objects.select_for_update().get_or_create(user=order.user)
    account.balance += points
    account.save(update_fields=["balance", "updated_at"])
    LoyaltyTransaction.objects.create(
        account=account,
        order=order,
        kind=LoyaltyTransaction.Kind.ORDER_REWARD,
        points=points,
        balance_after=account.balance,
        note=f"Hoàn tất đơn {order.number}",
    )
    return points
