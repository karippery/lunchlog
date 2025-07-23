from rest_framework.permissions import BasePermission, SAFE_METHODS
from apps.users.roles import UserRoles


class BaseRolePermission(BasePermission):
    """Base class for role-based permissions"""
    allowed_roles = []
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in self.allowed_roles
        )


class IsAdmin(BaseRolePermission):
    """Allow access only to users with the ADMIN role."""
    allowed_roles = [UserRoles.ADMIN]


class IsManager(BaseRolePermission):
    """Allow access only to users with the MANAGER role."""
    allowed_roles = [UserRoles.MANAGER]


class IsAdminOrManager(BaseRolePermission):
    """Allow access to ADMIN or MANAGER users."""
    allowed_roles = [UserRoles.ADMIN, UserRoles.MANAGER]


class IsSelfOrAdmin(BasePermission):
    """
    Allow users to edit only their own info.
    Admins can access all users.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.role == UserRoles.ADMIN or obj == request.user


class IsReadOnly(BasePermission):
    """
    Allow only read-only access (GET, HEAD, OPTIONS).
    """
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class IsAdminToDelete(BaseRolePermission):
    """
    Allow delete only if user is admin.
    """
    allowed_roles = [UserRoles.ADMIN]
    
    def has_permission(self, request, view):
        if request.method == 'DELETE':
            return super().has_permission(request, view)
        return True


class IsReceiptOwner(BasePermission):
    """Allow access only to the owner of the receipt."""
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user