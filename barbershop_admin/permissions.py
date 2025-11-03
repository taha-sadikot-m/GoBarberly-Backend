"""
Permission classes for Admin functionality
"""
from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Permission to only allow admin users to access the view.
    """
    message = "You do not have permission to perform this action. Admin access required."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'admin'
        )


class IsAdminOrSuperAdmin(permissions.BasePermission):
    """
    Permission to allow admin and super admin users to access the view.
    """
    message = "You do not have permission to perform this action. Admin access required."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['admin', 'super_admin']
        )


class CanManageOwnBarbershops(permissions.BasePermission):
    """
    Permission to check if admin can manage barbershops they created.
    Super admins can manage all barbershops, admins can only manage their own.
    """
    message = "You do not have permission to manage this barbershop."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['admin', 'super_admin']
        )
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Super admin can manage all barbershops
        if user.role == 'super_admin':
            return True
            
        # Admin can only manage barbershops they created
        if user.role == 'admin':
            return obj.created_by == user
            
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission to allow admin full access, others read-only access.
    """
    message = "You do not have permission to modify this resource. Admin access required."
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Read permissions for authenticated users
        if request.method in permissions.READONLY_METHODS:
            return True
            
        # Write permissions only for admin or super admin
        return request.user.role in ['admin', 'super_admin']


class CanViewOwnData(permissions.BasePermission):
    """
    Permission to ensure admins can only view data related to their barbershops.
    """
    message = "You do not have permission to view this data."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['admin', 'super_admin']
        )
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Super admin can view all data
        if user.role == 'super_admin':
            return True
            
        # Admin can only view data from their barbershops
        if user.role == 'admin':
            # Check if object has barbershop attribute
            if hasattr(obj, 'barbershop'):
                return obj.barbershop.created_by == user
            
            # Check if object is a barbershop
            elif hasattr(obj, 'created_by'):
                return obj.created_by == user
                
        return False


class CanManageAppointments(permissions.BasePermission):
    """
    Permission to manage appointments - admins can manage appointments 
    for barbershops they created.
    """
    message = "You do not have permission to manage appointments for this barbershop."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['admin', 'super_admin']
        )
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Super admin can manage all appointments
        if user.role == 'super_admin':
            return True
            
        # Admin can only manage appointments for their barbershops
        if user.role == 'admin':
            return obj.barbershop.created_by == user
            
        return False