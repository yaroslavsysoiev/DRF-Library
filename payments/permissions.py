from rest_framework import permissions


class PaymentPermissions(permissions.BasePermission):
    """
    Custom permissions for Payment model.
    - Users can only see their own payments
    - Admins can see all payments
    - Only authenticated users can access payments
    """
    
    def has_permission(self, request, view):
        # Require authentication for all operations
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Users can only access their own payments
        # Admins can access all payments
        return obj.user == request.user or request.user.is_staff


class PaymentCreatePermissions(permissions.BasePermission):
    """
    Permissions for creating payments.
    - Only authenticated users can create payments
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated