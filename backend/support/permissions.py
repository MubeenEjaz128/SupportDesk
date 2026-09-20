from rest_framework.permissions import BasePermission

def user_role(user):
    if getattr(user, 'is_superuser', False): return 'admin'
    try: return user.agent_profile.role
    except Exception: return 'agent'

class IsSupervisorOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and user_role(request.user) in {'admin','supervisor'})

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and user_role(request.user) == 'admin')
