from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'superadmin'
    
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'superadmin']
    
class IsEditor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['editor', 'admin', 'superadmin']
    
class IsJournalist(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['journalist', 'editor', 'admin', 'superadmin']
    
class IsReader(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['reader', 'journalist', 'editor', 'admin', 'superadmin']


class HasRole(BasePermission):
    """Permission that checks whether the user has any of the given roles.

    Instantiate with a list of role strings, e.g. `HasRole(['admin','editor'])`.
    """
    def __init__(self, roles=None):
        self.roles = roles or []

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in self.roles