from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.db import transaction

from apps.accounts.roles import BusinessRole

User = get_user_model()


@transaction.atomic
def create_staff(*, email: str, full_name: str, password: str) -> User:
    normalized_email = User.objects.normalize_email_address(email)
    candidate = User(email=normalized_email, full_name=full_name)
    validate_password(password, user=candidate)
    user = User.objects.create_user(
        email=normalized_email,
        full_name=full_name,
        password=password,
        is_staff=True,
        is_active=True,
    )
    group, _ = Group.objects.get_or_create(name=BusinessRole.STAFF)
    user.groups.set([group])
    return user


@transaction.atomic
def update_staff(
    *, staff: User, full_name: str | None = None, is_active: bool | None = None
) -> User:
    staff = User.objects.select_for_update().get(pk=staff.pk)
    fields = []
    if full_name is not None:
        staff.full_name = full_name
        fields.append("full_name")
    if is_active is not None:
        staff.is_active = is_active
        fields.append("is_active")
    staff.is_staff = True
    fields.append("is_staff")
    staff.save(update_fields=fields)
    group, _ = Group.objects.get_or_create(name=BusinessRole.STAFF)
    staff.groups.set([group])
    return staff
