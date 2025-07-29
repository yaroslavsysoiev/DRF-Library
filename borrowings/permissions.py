from rest_framework import permissions


class BorrowingPermissions(permissions.BasePermission):
    """
    Custom permissions for Borrowing model.
    - Users can only see their own borrowings
    - Admins can see all borrowings
    - Only authenticated users can access borrowings
    """
    
    def has_permission(self, request, view):
        # Require authentication for all operations
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Users can only access their own borrowings
        # Admins can access all borrowings
        return obj.user == request.user or request.user.is_staff


class BorrowingCreatePermissions(permissions.BasePermission):
    """
    Permissions for creating borrowings.
    - Only authenticated users can create borrowings
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated