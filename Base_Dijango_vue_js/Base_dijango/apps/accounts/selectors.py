from django.contrib.auth import get_user_model

User = get_user_model()


def get_active_user_by_id(*, user_id: int) -> User | None:
    return User.objects.filter(id=user_id, is_active=True).first()
