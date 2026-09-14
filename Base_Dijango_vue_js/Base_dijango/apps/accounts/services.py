from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


@transaction.atomic
def update_profile(*, user: User, full_name: str) -> User:
    user.full_name = full_name.strip()
    user.full_clean(exclude=["password"])
    user.save(update_fields=["full_name"])
    return user
