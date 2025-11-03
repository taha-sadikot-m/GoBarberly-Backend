"""
Permission classes for Super Admin functionality
"""
from rest_framework import permissions


class IsSuperAdmin(permissions.BasePermission):
    """
    Permission to only allow super admin users to access the view.
    """
    message = "You do not have permission to perform this action. Super Admin access required."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'super_admin'
        )


class IsSuperAdminOrAdmin(permissions.BasePermission):
    """
    Permission to allow super admin and admin users to access the view.
    """
    message = "You do not have permission to perform this action. Admin access required."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['super_admin', 'admin']
        )


class IsSuperAdminOrReadOnly(permissions.BasePermission):
    """
    Permission to allow super admin full access, others read-only access.
    """
    message = "You do not have permission to modify this resource. Super Admin access required."
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Read permissions for authenticated users
        if request.method in permissions.READONLY_METHODS:
            return True
            
        # Write permissions only for super admin
        return request.user.role == 'super_admin'


class CanManageUser(permissions.BasePermission):
    """
    Permission to check if user can manage other users based on hierarchy:
    - Super Admin can manage everyone
    - Admin can manage barbershops and customers
    - Barbershop can manage their own data only
    """
    message = "You do not have permission to manage this user."
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Super admin can manage everyone
        if user.role == 'super_admin':
            return True
            
        # Admin can manage barbershops and customers, but not other admins or super admins
        if user.role == 'admin':
            return obj.role in ['barbershop', 'customer', 'barber']
            
        # Barbershop can only manage their own profile
        if user.role == 'barbershop':
            return obj.id == user.id
            
        # Others cannot manage users
        return False


class CanCreateUserRole(permissions.BasePermission):
    """
    Permission to check if user can create users with specific roles:
    - Super Admin can create admins and barbershops
    - Admin can create barbershops only
    """
    message = "You do not have permission to create users with this role."
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Get the role from request data
        role = request.data.get('role', '').lower()
        user_role = request.user.role
        
        # Super admin can create admins and barbershops
        if user_role == 'super_admin':
            return role in ['admin', 'barbershop']
            
        # Admin can create barbershops only
        if user_role == 'admin':
            return role == 'barbershop'
            
        return False