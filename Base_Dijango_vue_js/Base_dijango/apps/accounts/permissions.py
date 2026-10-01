from rest_framework.permissions import BasePermission

from .roles import BusinessRole, get_business_roles


class IsStaffOrAdmin(BasePermission):
    message = "Bạn không có quyền truy cập khu vực quản trị."

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        roles = set(get_business_roles(request.user))
        return bool(roles.intersection({BusinessRole.STAFF, BusinessRole.ADMIN}))


class IsAdmin(BasePermission):
    message = "Bạn cần quyền ADMIN để thực hiện thao tác này."

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        return BusinessRole.ADMIN in set(get_business_roles(request.user))


class IsCustomer(BasePermission):
    message = "Bạn cần tài khoản CUSTOMER để thực hiện thao tác này."

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        return BusinessRole.CUSTOMER in set(get_business_roles(request.user))
