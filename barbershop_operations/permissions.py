"""
Permission classes for Barbershop Operations
"""
from rest_framework import permissions


class IsBarbershop(permissions.BasePermission):
    """
    Permission that only allows access to users with barbershop role.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'role') and 
            request.user.role == 'barbershop'
        )


class CanAccessOwnBarbershopData(permissions.BasePermission):
    """
    Permission that only allows barbershop users to access their own data.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'role') and 
            request.user.role == 'barbershop'
        )
    
    def has_object_permission(self, request, view, obj):
        # Check if object has barbershop field and belongs to current user
        if hasattr(obj, 'barbershop'):
            return obj.barbershop == request.user
        
        # Check if object has staff field (for staff availability)
        if hasattr(obj, 'staff'):
            return obj.staff.barbershop == request.user
        
        return False


class IsBarbershopOrReadOnly(permissions.BasePermission):
    """
    Permission that allows read access to any authenticated user,
    but write access only to barbershop users.
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        return (
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'role') and 
            request.user.role == 'barbershop'
        )