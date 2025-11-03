"""
Views for Admin functionality
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import Activity, Appointment, AdminReport
from .serializers import (
    AdminStatsSerializer, ActivitySerializer, AppointmentSerializer,
    AppointmentCreateSerializer, AdminBarbershopListSerializer,
    AdminBarbershopCreateSerializer, AdminBarbershopUpdateSerializer,
    AdminDashboardDataSerializer
)
from .permissions import (
    IsAdmin, IsAdminOrSuperAdmin, CanManageOwnBarbershops, CanViewOwnData
)
from super_admin.models import Subscription


User = get_user_model()


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for admin views"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ActivityPagination(PageNumberPagination):
    """Pagination for activity feed"""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsAdmin])
def admin_dashboard_stats(request):
    """
    Get admin dashboard statistics (scoped to admin's barbershops)
    """
    admin = request.user
    
    # Get barbershops created by this admin
    barbershops = User.objects.filter(
        created_by=admin,
        role='barbershop'
    )
    
    # Calculate stats
    total_barbershops = barbershops.count()
    active_barbershops = barbershops.filter(is_active=True).count()
    
    # Get appointments for admin's barbershops
    total_appointments = Appointment.objects.filter(
        barbershop__in=barbershops
    ).count()
    
    # Calculate monthly revenue
    current_month = timezone.now().replace(day=1)
    monthly_revenue = Appointment.objects.filter(
        barbershop__in=barbershops,
        appointment_date__gte=current_month,
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    stats_data = {
        'total_barbershops': total_barbershops,
        'active_barbershops': active_barbershops,
        'total_appointments': total_appointments,
        'monthly_revenue': monthly_revenue
    }
    
    serializer = AdminStatsSerializer(stats_data)
    return Response({
        'success': True,
        'data': serializer.data,
        'message': 'Dashboard statistics retrieved successfully'
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsAdmin])
def admin_dashboard_data(request):
    """
    Get complete admin dashboard data
    """
    admin = request.user
    
    # Get barbershops created by this admin
    barbershops = User.objects.filter(
        created_by=admin,
        role='barbershop'
    ).order_by('-created_at')
    
    # Get stats
    total_barbershops = barbershops.count()
    active_barbershops = barbershops.filter(is_active=True).count()
    total_appointments = Appointment.objects.filter(barbershop__in=barbershops).count()
    
    current_month = timezone.now().replace(day=1)
    monthly_revenue = Appointment.objects.filter(
        barbershop__in=barbershops,
        appointment_date__gte=current_month,
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    stats_data = {
        'total_barbershops': total_barbershops,
        'active_barbershops': active_barbershops,
        'total_appointments': total_appointments,
        'monthly_revenue': monthly_revenue
    }
    
    # Get recent activities (last 10)
    recent_activities = Activity.objects.filter(
        barbershop__in=barbershops
    ).order_by('-timestamp')[:10]
    
    # Get recent appointments (last 10)
    recent_appointments = Appointment.objects.filter(
        barbershop__in=barbershops
    ).order_by('-created_at')[:10]
    
    # Serialize data
    dashboard_data = {
        'stats': AdminStatsSerializer(stats_data).data,
        'recent_activities': ActivitySerializer(recent_activities, many=True).data,
        'recent_appointments': AppointmentSerializer(recent_appointments, many=True).data,
        'barbershop_summary': AdminBarbershopListSerializer(barbershops[:5], many=True).data
    }
    
    return Response({
        'success': True,
        'data': dashboard_data,
        'message': 'Dashboard data retrieved successfully'
    })


class ActivityListView(generics.ListAPIView):
    """
    List activities for admin's barbershops with pagination
    """
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    pagination_class = ActivityPagination
    
    def get_queryset(self):
        """Get activities for admin's barbershops"""
        admin = self.request.user
        barbershops = User.objects.filter(created_by=admin, role='barbershop')
        
        queryset = Activity.objects.filter(
            barbershop__in=barbershops
        ).order_by('-timestamp')
        
        # Filter by action type if provided
        action_type = self.request.query_params.get('action_type')
        if action_type:
            queryset = queryset.filter(action_type=action_type)
        
        # Filter by barbershop if provided
        barbershop_id = self.request.query_params.get('barbershop')
        if barbershop_id:
            queryset = queryset.filter(barbershop_id=barbershop_id)
        
        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(timestamp__date__gte=start_date)
            except ValueError:
                pass
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(timestamp__date__lte=end_date)
            except ValueError:
                pass
        
        return queryset


class AppointmentListCreateView(generics.ListCreateAPIView):
    """
    List and create appointments for admin's barbershops
    """
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    pagination_class = StandardResultsSetPagination
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AppointmentCreateSerializer
        return AppointmentSerializer
    
    def get_queryset(self):
        """Get appointments for admin's barbershops"""
        admin = self.request.user
        barbershops = User.objects.filter(created_by=admin, role='barbershop')
        
        queryset = Appointment.objects.filter(
            barbershop__in=barbershops
        ).order_by('-appointment_date')
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by barbershop if provided
        barbershop_id = self.request.query_params.get('barbershop')
        if barbershop_id:
            queryset = queryset.filter(barbershop_id=barbershop_id)
        
        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(appointment_date__date__gte=start_date)
            except ValueError:
                pass
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(appointment_date__date__lte=end_date)
            except ValueError:
                pass
        
        return queryset


class AppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete an appointment (admin scoped)
    """
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin, CanViewOwnData]
    
    def get_queryset(self):
        """Get appointments for admin's barbershops"""
        admin = self.request.user
        barbershops = User.objects.filter(created_by=admin, role='barbershop')
        return Appointment.objects.filter(barbershop__in=barbershops)


class AdminBarbershopListCreateView(generics.ListCreateAPIView):
    """
    List and create barbershops (admin scoped)
    """
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    pagination_class = StandardResultsSetPagination
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AdminBarbershopCreateSerializer
        return AdminBarbershopListSerializer
    
    def get_queryset(self):
        """Get barbershops created by this admin"""
        admin = self.request.user
        queryset = User.objects.filter(
            created_by=admin,
            role='barbershop'
        ).order_by('-created_at')
        
        # Search functionality
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(shop_name__icontains=search) |
                Q(shop_owner_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter == 'active':
            queryset = queryset.filter(is_active=True)
        elif status_filter == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        # Filter by subscription plan
        plan_filter = self.request.query_params.get('plan')
        if plan_filter:
            queryset = queryset.filter(subscription__plan=plan_filter)
        
        return queryset

    def list(self, request, *args, **kwargs):
        """List barbershops with custom response format"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'count': queryset.count(),
            'message': 'Barbershops retrieved successfully'
        })

    def create(self, request, *args, **kwargs):
        """Create barbershop with custom response format"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            barbershop = serializer.save()
            response_serializer = AdminBarbershopListSerializer(barbershop)
            
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


class AdminBarbershopDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a barbershop (admin scoped)
    """
    permission_classes = [permissions.IsAuthenticated, IsAdmin, CanManageOwnBarbershops]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return AdminBarbershopUpdateSerializer
        return AdminBarbershopListSerializer
    
    def get_queryset(self):
        """Get active barbershops created by this admin"""
        admin = self.request.user
        return User.objects.active_with_role('barbershop').filter(created_by=admin)
    
    def perform_destroy(self, instance):
        """Soft delete barbershop"""
        instance.soft_delete(deleted_by=self.request.user)
        
        # Create activity log
        Activity.objects.create(
            barbershop=instance,
            action_type='profile_updated',
            description=f"Barbershop deactivated by {self.request.user.get_full_name()}",
            metadata={
                'deactivated_by': self.request.user.id,
                'action': 'deactivate'
            }
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsAdmin])
def toggle_barbershop_status(request, barbershop_id):
    """
    Toggle barbershop active status (admin scoped)
    """
    admin = request.user
    
    try:
        barbershop = User.objects.get(
            id=barbershop_id,
            created_by=admin,
            role='barbershop'
        )
    except User.DoesNotExist:
        return Response(
            {'error': 'Barbershop not found or you do not have permission to manage it.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Toggle status
    barbershop.is_active = not barbershop.is_active
    barbershop.save()
    
    # Create activity log
    action = 'activated' if barbershop.is_active else 'deactivated'
    Activity.objects.create(
        barbershop=barbershop,
        action_type='profile_updated',
        description=f"Barbershop {action} by {admin.get_full_name()}",
        metadata={
            'updated_by': admin.id,
            'action': action,
            'new_status': barbershop.is_active
        }
    )
    
    return Response({
        'message': f'Barbershop {action} successfully.',
        'is_active': barbershop.is_active
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsAdmin])
def admin_barbershop_analytics(request, barbershop_id):
    """
    Get analytics for a specific barbershop (admin scoped)
    """
    admin = request.user
    
    try:
        barbershop = User.objects.get(
            id=barbershop_id,
            created_by=admin,
            role='barbershop'
        )
    except User.DoesNotExist:
        return Response(
            {'error': 'Barbershop not found or you do not have permission to view it.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get time range from query params (default to last 30 days)
    days = int(request.query_params.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    # Calculate analytics
    appointments = Appointment.objects.filter(
        barbershop=barbershop,
        appointment_date__gte=start_date
    )
    
    total_appointments = appointments.count()
    completed_appointments = appointments.filter(status='completed').count()
    total_revenue = appointments.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    
    # Monthly breakdown
    monthly_data = []
    current_date = start_date.replace(day=1)
    while current_date <= timezone.now():
        next_month = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        month_appointments = appointments.filter(
            appointment_date__gte=current_date,
            appointment_date__lt=next_month
        )
        month_revenue = month_appointments.filter(status='completed').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        monthly_data.append({
            'month': current_date.strftime('%Y-%m'),
            'appointments': month_appointments.count(),
            'revenue': month_revenue
        })
        current_date = next_month
    
    analytics_data = {
        'barbershop': AdminBarbershopListSerializer(barbershop).data,
        'period_days': days,
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
        'completion_rate': (completed_appointments / total_appointments * 100) if total_appointments > 0 else 0,
        'total_revenue': total_revenue,
        'average_revenue_per_appointment': (total_revenue / completed_appointments) if completed_appointments > 0 else Decimal('0.00'),
        'monthly_breakdown': monthly_data,
        'recent_activities': ActivitySerializer(
            barbershop.activities.order_by('-timestamp')[:10],
            many=True
        ).data
    }
    
    return Response(analytics_data)


class ArchivedBarbershopListView(generics.ListAPIView):
    """
    List archived (soft-deleted) barbershops for regular admin
    """
    serializer_class = AdminBarbershopListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get archived barbershops created by this admin"""
        admin = self.request.user
        if admin.role != 'admin':
            return User.objects.none()
        return User.objects.deleted_with_role('barbershop').filter(created_by=admin).order_by('-deleted_at')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'success': True,
            'message': 'Archived barbershops retrieved successfully',
            'count': queryset.count(),
            'barbershops': serializer.data
        })


class RestoreBarbershopView(APIView):
    """
    Restore a soft-deleted barbershop (admin only)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({
                'success': False,
                'message': 'user_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get the soft-deleted barbershop (must be created by this admin)
            admin = self.request.user
            if admin.role != 'admin':
                return Response({
                    'success': False,
                    'message': 'Permission denied'
                }, status=status.HTTP_403_FORBIDDEN)
            
            barbershop = User.objects.deleted_with_role('barbershop').get(
                id=user_id, 
                created_by=admin
            )
            
            # Restore the barbershop
            barbershop.restore()
            
            return Response({
                'success': True,
                'message': f'Barbershop {barbershop.shop_name or barbershop.email} restored successfully',
                'barbershop': {
                    'id': barbershop.id,
                    'email': barbershop.email,
                    'shop_name': barbershop.shop_name,
                    'shop_owner_name': barbershop.shop_owner_name,
                    'is_active': barbershop.is_active,
                    'restored_at': timezone.now().isoformat()
                }
            })
            
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Archived barbershop not found or not created by you'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Failed to restore barbershop: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TransferBarbershopOwnershipView(APIView):
    """
    Transfer barbershop ownership to another admin
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperAdmin]
    
    def post(self, request, *args, **kwargs):
        """Transfer barbershop ownership from current admin to another admin"""
        try:
            from_admin = request.user
            barbershop_id = request.data.get('barbershop_id')
            to_admin_id = request.data.get('to_admin_id')
            
            if not barbershop_id or not to_admin_id:
                return Response({
                    'success': False,
                    'message': 'Both barbershop_id and to_admin_id are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get the barbershop to transfer
            try:
                if from_admin.role == 'super_admin':
                    # Super admin can transfer any barbershop
                    barbershop = User.objects.active_with_role('barbershop').get(id=barbershop_id)
                else:
                    # Regular admin can only transfer barbershops they created
                    barbershop = User.objects.active_with_role('barbershop').get(
                        id=barbershop_id,
                        created_by=from_admin
                    )
            except User.DoesNotExist:
                error_message = 'Barbershop not found'
                if from_admin.role == 'admin':
                    error_message += ' or not owned by you'
                return Response({
                    'success': False,
                    'message': error_message
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Get the target admin
            try:
                to_admin = User.objects.active_with_role('admin').get(id=to_admin_id)
            except User.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Target admin not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Prevent transferring to self
            if from_admin.id == to_admin.id:
                return Response({
                    'success': False,
                    'message': 'Cannot transfer barbershop to yourself'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Perform the transfer
            barbershop.created_by = to_admin
            barbershop.save()
            
            # Log the transfer activity
            Activity.objects.create(
                barbershop=barbershop,
                action_type='transfer_out',
                description=f'Barbershop "{barbershop.shop_name}" transferred from {from_admin.get_full_name() or from_admin.email} to {to_admin.get_full_name() or to_admin.email}',
                metadata={
                    'barbershop_id': barbershop.id,
                    'barbershop_name': barbershop.shop_name,
                    'from_admin_id': from_admin.id,
                    'from_admin_email': from_admin.email,
                    'from_admin_name': f"{from_admin.first_name} {from_admin.last_name}".strip(),
                    'to_admin_id': to_admin.id,
                    'to_admin_email': to_admin.email,
                    'to_admin_name': f"{to_admin.first_name} {to_admin.last_name}".strip(),
                    'transfer_type': 'ownership_change'
                }
            )
            
            return Response({
                'success': True,
                'message': f'Successfully transferred "{barbershop.shop_name}" to {to_admin.first_name} {to_admin.last_name} ({to_admin.email})',
                'data': {
                    'barbershop': {
                        'id': barbershop.id,
                        'shop_name': barbershop.shop_name,
                        'shop_owner_name': barbershop.shop_owner_name,
                        'email': barbershop.email
                    },
                    'from_admin': {
                        'id': from_admin.id,
                        'name': f"{from_admin.first_name} {from_admin.last_name}".strip(),
                        'email': from_admin.email
                    },
                    'to_admin': {
                        'id': to_admin.id,
                        'name': f"{to_admin.first_name} {to_admin.last_name}".strip(),
                        'email': to_admin.email
                    }
                }
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Failed to transfer barbershop: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AvailableAdminsForTransferView(generics.ListAPIView):
    """
    Get list of available admins for barbershop transfer (excluding current admin)
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperAdmin]
    
    def get(self, request, *args, **kwargs):
        """Get list of active admins for transfer selection"""
        try:
            current_admin = request.user
            
            # Get all active admins except current user
            available_admins = User.objects.active_with_role('admin').exclude(
                id=current_admin.id
            ).values(
                'id', 'email', 'first_name', 'last_name'
            )
            
            # Format the response
            admins_list = []
            for admin in available_admins:
                admins_list.append({
                    'id': admin['id'],
                    'name': f"{admin['first_name']} {admin['last_name']}".strip() or admin['email'],
                    'email': admin['email'],
                    'display_name': f"{admin['first_name']} {admin['last_name']}".strip() + f" ({admin['email']})"
                })
            
            return Response({
                'success': True,
                'message': 'Available admins retrieved successfully',
                'count': len(admins_list),
                'admins': admins_list
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Failed to get available admins: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
