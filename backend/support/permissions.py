from rest_framework.permissions import BasePermission


STAFF_ROLES = {'admin', 'supervisor', 'agent'}
MANAGEMENT_ROLES = {'admin', 'supervisor'}


def user_role(user):
    if not user or not getattr(user, 'is_authenticated', False):
        return None
    if getattr(user, 'is_superuser', False):
        return 'admin'
    try:
        return user.agent_profile.role
    except Exception:
        return 'agent'


def customer_for_user(user):
    try:
        if user_role(user) == 'customer':
            return user.agent_profile.customer
    except Exception:
        pass
    return None


class IsSupervisorOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(user_role(request.user) in MANAGEMENT_ROLES)


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(user_role(request.user) == 'admin')


class IsSupportStaff(BasePermission):
    def has_permission(self, request, view):
        return bool(user_role(request.user) in STAFF_ROLES)


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return bool(user_role(request.user) == 'customer')
