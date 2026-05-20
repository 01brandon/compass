from rest_framework.permissions import BasePermission, SAFE_METHODS

class ArticlePermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True  # Allow read-only access for all users
        if not request.user.is_authenticated:
            return False  # Deny write access for unauthenticated users
        return (
            request.user.role in [
                'journalist', 
                'editor',
                'admin', 
                'superadmin'
            ])  # Allow write access for journalists and above
        
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True  # Allow read-only access for all users
        if not request.user.is_authenticated:
            return False  # Deny write access for unauthenticated users
        if request.user.role in ['editor', 'admin', 'superadmin']:
            return True  # Editors and above can edit any article
        if request.user.role == 'journalist':
            return obj.author == request.user  # Journalists can only edit their own articles
        return False  # Deny write access for readers and other roles