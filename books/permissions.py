from rest_framework import permissions


class BookPermissions(permissions.BasePermission):
    """
    Custom permissions for Book model.
    - List: All users (including unauthenticated)
    - Create/Update/Delete: Admin users only
    """
    
    def has_permission(self, request, view):
        # Allow list for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Require authentication for other methods
        if not request.user.is_authenticated:
            return False
        
        # Require admin for create/update/delete
        return request.user.is_staff
    
    def has_object_permission(self, request, view, obj):
        # Allow read for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Require admin for update/delete
        return request.user.is_staff