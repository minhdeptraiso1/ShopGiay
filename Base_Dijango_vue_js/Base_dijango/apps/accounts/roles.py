from enum import StrEnum


class BusinessRole(StrEnum):
    CUSTOMER = "CUSTOMER"
    STAFF = "STAFF"
    ADMIN = "ADMIN"


BUSINESS_ROLE_NAMES = frozenset(role.value for role in BusinessRole)


def get_business_roles(user) -> list[str]:
    if user.is_superuser:
        return [BusinessRole.ADMIN]
    return sorted(user.groups.filter(name__in=BUSINESS_ROLE_NAMES).values_list("name", flat=True))
