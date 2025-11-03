"""
Super Admin API Views
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.db.models import Count, Q, Sum
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import Subscription, SubscriptionHistory
from .serializers import (
    SuperAdminStatsSerializer,
    AdminListSerializer,
    AdminCreateSerializer,
    AdminUpdateSerializer,
    BarbershopListSerializer,
    BarbershopCreateSerializer,
    BarbershopUpdateSerializer,
    BarbershopDetailSerializer,
    ArchivedAdminSerializer,
    ArchivedBarbershopSerializer,
    UserStatusToggleSerializer,
    SubscriptionSerializer
)
from .permissions import IsSuperAdmin, IsSuperAdminOrAdmin, CanManageUser

User = get_user_model()


class DashboardStatsView(APIView):
    """
    Get Super Admin dashboard statistics
    """
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]
    
    def get(self, request):
        """
        Get dashboard statistics for super admin
        """
        try:
            # Calculate statistics
            total_admins = User.objects.filter(role='admin').count()
            total_barbershops = User.objects.filter(role='barbershop').count()
            active_barbershops = User.objects.filter(
                role='barbershop', 
                is_active=True
            ).count()
            
            # Calculate total revenue (mock calculation - replace with actual logic)
            # This would typically come from a payments/transactions model
            total_revenue = Decimal('125000.00')  # Mock data
            
            # Calculate monthly growth (mock calculation)
            current_month_barbershops = User.objects.filter(
                role='barbershop',
                created_at__gte=timezone.now().replace(day=1)
            ).count()
            
            last_month = timezone.now().replace(day=1) - timedelta(days=1)
            last_month_barbershops = User.objects.filter(
                role='barbershop',
                created_at__gte=last_month.replace(day=1),
                created_at__lt=timezone.now().replace(day=1)
            ).count()
            
            if last_month_barbershops > 0:
                monthly_growth = ((current_month_barbershops - last_month_barbershops) / last_month_barbershops) * 100
            else:
                monthly_growth = 100.0 if current_month_barbershops > 0 else 0.0
            
            stats_data = {
                'total_admins': total_admins,
                'total_barbershops': total_barbershops,
                'active_barbershops': active_barbershops,
                'total_revenue': total_revenue,
                'monthly_growth': round(monthly_growth, 1)
            }
            
            serializer = SuperAdminStatsSerializer(stats_data)
            
            return Response({
                'success': True,
                'data': serializer.data,
                'message': 'Dashboard statistics retrieved successfully'
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error retrieving dashboard statistics: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminListCreateView(generics.ListCreateAPIView):
    """
    List all admins or create a new admin
    """
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]
    
    def get_queryset(self):
        return User.objects.active_with_role('admin').order_by('-created_at')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AdminCreateSerializer
        return AdminListSerializer
    
    def list(self, request, *args, **kwargs):
        """List all admins"""
        queryset = self.get_queryset()
        
        # Add search functionality
        search = request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        # Add status filter
        is_active = request.query_params.get('is_active', '')
        if is_active in ['true', 'false']:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'count': queryset.count(),
            'message': 'Admins retrieved successfully'
        })
    
    def create(self, request, *args, **kwargs):
        """Create a new admin"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            admin = serializer.save()
            response_serializer = AdminListSerializer(admin)
            
            return Response({
                'success': True,
                'data': response_serializer.data,
                'message': 'Admin created successfully'
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'errors': serializer.errors,
            'message': 'Failed to create admin'
        }, status=status.HTTP_400_BAD_REQUEST)


class AdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete an admin
    """
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]
    queryset = User.objects.active_with_role('admin')
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return AdminUpdateSerializer
        return AdminListSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """Get admin details"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Admin details retrieved successfully'
        })
    
    def update(self, request, *args, **kwargs):
        """Update admin"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            admin = serializer.save()
            response_serializer = AdminListSerializer(admin)
            
            return Response({
                'success': True,
                'data': response_serializer.data,
                'message': 'Admin updated successfully'
            })
        
        return Response({
            'success': False,
            'errors': serializer.errors,
            'message': 'Failed to update admin'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """Delete admin"""
        instance = self.get_object()
        
        # Check if admin has created any barbershops (only active ones)
        created_barbershops = User.objects.active_with_role('barbershop').filter(created_by=instance)
        created_count = created_barbershops.count()
        
        if created_count > 0:
            # Get barbershop names for better error message
            barbershop_names = list(created_barbershops.values_list('shop_name', flat=True)[:3])
            names_display = ', '.join([name or 'Unnamed Shop' for name in barbershop_names])
            if created_count > 3:
                names_display += f' and {created_count - 3} more'
            
            return Response({
                'success': False,
                'message': f'Cannot delete admin. They have created {created_count} barbershop(s): {names_display}. Transfer ownership first.',
                'data': {
                    'barbershop_count': created_count,
                    'barbershop_names': barbershop_names,
                    'admin_id': instance.id,
                    'admin_email': instance.email
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        admin_email = instance.email
        # Soft delete instead of hard delete
        instance.soft_delete(deleted_by=self.request.user)
        
        return Response({
            'success': True,
            'message': f'Admin {admin_email} archived successfully'
        })


class AdminToggleStatusView(APIView):
    """
    Toggle admin active status
    """
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]
    
    def patch(self, request, pk):
        """Toggle admin active status"""
        try:
            admin = User.objects.get(pk=pk, role='admin')
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Admin not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Toggle status
        admin.is_active = not admin.is_active
        admin.save()
        
        serializer = AdminListSerializer(admin)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'message': f'Admin {"activated" if admin.is_active else "deactivated"} successfully'
        })


class AdminTransferOwnershipView(APIView):
    """
    Transfer barbershop ownership between admins
    """
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]
    
    def post(self, request, pk):
        """Transfer barbershop ownership from one admin to another"""
        try:
            # Get the admin whose barbershops we're transferring
            from_admin = User.objects.get(pk=pk, role='admin')
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Source admin not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get target admin ID from request
        to_admin_id = request.data.get('to_admin_id')
        if not to_admin_id:
            return Response({
                'success': False,
                'message': 'Target admin ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            to_admin = User.objects.get(pk=to_admin_id, role='admin', is_active=True)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Target admin not found or inactive'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get barbershops created by the source admin
        barbershops_to_transfer = User.objects.active_with_role('barbershop').filter(created_by=from_admin)
        transfer_count = barbershops_to_transfer.count()
        
        if transfer_count == 0:
            return Response({
                'success': False,
                'message': 'No barbershops to transfer'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Perform the transfer
        with transaction.atomic():
            updated_count = barbershops_to_transfer.update(created_by=to_admin)
            
            # Get barbershop names for response
            barbershop_names = list(barbershops_to_transfer.values_list('shop_name', flat=True)[:5])
            names_display = ', '.join([name or 'Unnamed Shop' for name in barbershop_names])
            if transfer_count > 5:
                names_display += f' and {transfer_count - 5} more'
        
        return Response({
            'success': True,
            'message': f'Successfully transferred {transfer_count} barbershop(s) from {from_admin.email} to {to_admin.email}',
            'data': {
                'transferred_count': updated_count,
                'from_admin': from_admin.email,
                'to_admin': to_admin.email,
                'barbershop_names': barbershop_names
            }
        })


class AdminBarbershopsView(APIView):
    """
    Get barbershops created by a specific admin
    """
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]
    
    def get(self, request, pk):
        """Get list of barbershops created by admin"""
        try:
            admin = User.objects.get(pk=pk, role='admin')
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Admin not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get barbershops created by this admin
        barbershops = User.objects.filter(created_by=admin, role='barbershop').select_related('subscription')
        serializer = BarbershopListSerializer(barbershops, many=True)
        
        return Response({
            'success': True,
            'data': {
                'admin': {
                    'id': admin.id,
                    'email': admin.email,
                    'name': f'{admin.first_name} {admin.last_name}'.strip()
                },
                'barbershops': serializer.data,
                'count': barbershops.count()
            },
            'message': f'Barbershops created by {admin.email} retrieved successfully'
        })


class BarbershopListCreateView(generics.ListCreateAPIView):
    """
    List all barbershops or create a new barbershop
    """
    permission_classes = [permissions.IsAuthenticated, IsSuperAdminOrAdmin]
    
    def get_queryset(self):
        return User.objects.active_with_role('barbershop').select_related('subscription').order_by('-created_at')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BarbershopCreateSerializer
        return BarbershopListSerializer
    
    def list(self, request, *args, **kwargs):
        """List all barbershops"""
        queryset = self.get_queryset()
        
        # Add search functionality
        search = request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(shop_name__icontains=search) |
                Q(shop_owner_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        # Add status filter
        is_active = request.query_params.get('is_active', '')
        if is_active in ['true', 'false']:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Add subscription plan filter
        plan = request.query_params.get('plan', '')
        if plan:
            queryset = queryset.filter(subscription__plan=plan)
        
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'count': queryset.count(),
            'message': 'Barbershops retrieved successfully'
        })
    
    def create(self, request, *args, **kwargs):
        """Create a new barbershop"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            barbershop = serializer.save()
            response_serializer = BarbershopListSerializer(barbershop)
            
            return Response({
                'success': True,
                'data': response_serializer.data,
                'message': 'Barbershop created successfully'
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'errors': serializer.errors,
            'message': 'Failed to create barbershop'
        }, status=status.HTTP_400_BAD_REQUEST)


class BarbershopDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a barbershop
    """
    permission_classes = [permissions.IsAuthenticated, IsSuperAdminOrAdmin]
    queryset = User.objects.active_with_role('barbershop').select_related('subscription')
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return BarbershopUpdateSerializer
        return BarbershopDetailSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """Get barbershop details"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Barbershop details retrieved successfully'
        })
    
    def update(self, request, *args, **kwargs):
        """Update barbershop"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            barbershop = serializer.save()
            response_serializer = BarbershopDetailSerializer(barbershop)
            
            return Response({
                'success': True,
                'data': response_serializer.data,
                'message': 'Barbershop updated successfully'
            })
        
        return Response({
            'success': False,
            'errors': serializer.errors,
            'message': 'Failed to update barbershop'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """Delete barbershop"""
        instance = self.get_object()
        
        # Check if barbershop has active subscription
        # Only prevent deletion if subscription status is 'active' and not expired
        if (hasattr(instance, 'subscription') and 
            instance.subscription.status == 'active' and 
            not instance.subscription.is_expired):
            return Response({
                'success': False,
                'message': 'Cannot delete barbershop with active subscription. Cancel subscription first.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        shop_name = instance.shop_name or instance.email
        # Soft delete instead of hard delete
        instance.soft_delete(deleted_by=self.request.user)
        
        return Response({
            'success': True,
            'message': f'Barbershop {shop_name} archived successfully'
        })


class BarbershopToggleStatusView(APIView):
    """
    Toggle barbershop active status
    """
    permission_classes = [permissions.IsAuthenticated, IsSuperAdminOrAdmin]
    
    def patch(self, request, pk):
        """Toggle barbershop active status"""
        try:
            barbershop = User.objects.get(pk=pk, role='barbershop')
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Barbershop not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Toggle status
        barbershop.is_active = not barbershop.is_active
        barbershop.save()
        
        serializer = BarbershopListSerializer(barbershop)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'message': f'Barbershop {"activated" if barbershop.is_active else "deactivated"} successfully'
        })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsSuperAdmin])
def load_dashboard_data(request):
    """
    Load all dashboard data in a single API call
    """
    try:
        # Get statistics
        total_admins = User.objects.filter(role='admin').count()
        total_barbershops = User.objects.filter(role='barbershop').count()
        active_barbershops = User.objects.filter(role='barbershop', is_active=True).count()
        total_revenue = Decimal('125000.00')  # Mock data
        monthly_growth = 15.2  # Mock data
        
        # Get recent admins
        recent_admins = User.objects.filter(role='admin').order_by('-created_at')[:5]
        admin_serializer = AdminListSerializer(recent_admins, many=True)
        
        # Get recent barbershops
        recent_barbershops = User.objects.filter(role='barbershop').select_related('subscription').order_by('-created_at')[:5]
        barbershop_serializer = BarbershopListSerializer(recent_barbershops, many=True)
        
        return Response({
            'success': True,
            'data': {
                'stats': {
                    'total_admins': total_admins,
                    'total_barbershops': total_barbershops,
                    'active_barbershops': active_barbershops,
                    'total_revenue': total_revenue,
                    'monthly_growth': monthly_growth
                },
                'recent_admins': admin_serializer.data,
                'recent_barbershops': barbershop_serializer.data
            },
            'message': 'Dashboard data loaded successfully'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error loading dashboard data: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ArchivedAdminListView(generics.ListAPIView):
    """
    List archived (soft-deleted) admins
    """
    serializer_class = ArchivedAdminSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    
    def get_queryset(self):
        return User.objects.deleted_with_role('admin').select_related('created_by', 'deleted_by').order_by('-deleted_at')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'success': True,
            'message': 'Archived admins retrieved successfully',
            'count': queryset.count(),
            'admins': serializer.data
        })


class ArchivedBarbershopListView(generics.ListAPIView):
    """
    List archived (soft-deleted) barbershops
    """
    serializer_class = ArchivedBarbershopSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    
    def get_queryset(self):
        return User.objects.deleted_with_role('barbershop').select_related('subscription', 'created_by', 'deleted_by').order_by('-deleted_at')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'success': True,
            'message': 'Archived barbershops retrieved successfully',
            'count': queryset.count(),
            'barbershops': serializer.data
        })


class RestoreUserView(APIView):
    """
    Restore a soft-deleted user (admin or barbershop)
    """
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    
    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        user_type = request.data.get('user_type')  # 'admin' or 'barbershop'
        
        if not user_id or not user_type:
            return Response({
                'success': False,
                'message': 'user_id and user_type are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get the soft-deleted user
            user = User.objects.deleted_with_role(user_type).get(id=user_id)
            
            # Restore the user
            user.restore()
            
            return Response({
                'success': True,
                'message': f'{user_type.title()} {user.email} restored successfully',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.get_full_name(),
                    'role': user.role,
                    'is_active': user.is_active,
                    'restored_at': timezone.now().isoformat()
                }
            })
            
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': f'Archived {user_type} not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Failed to restore {user_type}: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
