"""
Views for Barbershop Operations
"""
from django.shortcuts import render
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count, Sum, Q, Avg, F
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import calendar
from rest_framework.pagination import PageNumberPagination

from .models import (
    BarbershopAppointment,
    BarbershopSale,
    BarbershopStaff,
    BarbershopCustomer,
    BarbershopInventory,
    BarbershopActivityLog,
    BarbershopStaffAvailability,
    BarbershopService
)
from .serializers import (
    BarbershopProfileSerializer,
    BarbershopAppointmentSerializer,
    BarbershopAppointmentListSerializer,
    BarbershopAppointmentCreateSerializer,
    BarbershopSaleSerializer,
    BarbershopSaleListSerializer,
    BarbershopSaleCreateSerializer,
    BarbershopStaffSerializer,
    BarbershopStaffListSerializer,
    BarbershopStaffCreateSerializer,
    BarbershopCustomerSerializer,
    BarbershopCustomerListSerializer,
    BarbershopCustomerCreateSerializer,
    BarbershopInventorySerializer,
    BarbershopInventoryListSerializer,
    BarbershopInventoryCreateSerializer,
    BarbershopActivityLogSerializer,
    BarbershopStaffAvailabilitySerializer,
    BarbershopDashboardStatsSerializer,
    DashboardStatsSerializer,
    MonthlyRevenueSerializer,
    ServicePopularitySerializer,
    StaffPerformanceSerializer,
    BarbershopReportsDataSerializer,
    CalendarDataSerializer,
    ScheduleGridSerializer,
    SalesAnalyticsSerializer,
    BarbershopServiceSerializer,
    BarbershopServiceListSerializer
)
from .permissions import IsBarbershop, CanAccessOwnBarbershopData
from django.contrib.auth import get_user_model

User = get_user_model()


# Profile Views
class BarbershopProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update barbershop profile
    """
    serializer_class = BarbershopProfileSerializer
    permission_classes = [IsBarbershop]
    
    def get_object(self):
        """Return the current barbershop user"""
        return self.request.user
    
    def retrieve(self, request, *args, **kwargs):
        """Get barbershop profile"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            
            return Response({
                'success': True,
                'message': 'Profile retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Failed to retrieve profile: {str(e)}',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, *args, **kwargs):
        """Update barbershop profile"""
        try:
            partial = kwargs.pop('partial', True)  # Allow partial updates
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            
            if serializer.is_valid():
                self.perform_update(serializer)
                
                return Response({
                    'success': True,
                    'message': 'Profile updated successfully',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Failed to update profile: {str(e)}',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Dashboard Views
@api_view(['GET'])
@permission_classes([IsBarbershop])
def dashboard_stats(request):
    """Get dashboard statistics for barbershop"""
    user = request.user
    today = timezone.now().date()
    
    # Appointment stats
    today_appointments = BarbershopAppointment.objects.filter(
        barbershop=user, 
        appointment_date=today
    ).count()
    
    pending_appointments = BarbershopAppointment.objects.filter(
        barbershop=user, 
        status='pending'
    ).count()
    
    completed_appointments = BarbershopAppointment.objects.filter(
        barbershop=user, 
        status='completed',
        appointment_date=today
    ).count()
    
    cancelled_appointments = BarbershopAppointment.objects.filter(
        barbershop=user, 
        status='cancelled',
        appointment_date=today
    ).count()
    
    # Sales stats
    today_sales = BarbershopSale.objects.filter(
        barbershop=user,
        sale_date=today
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    total_sales = BarbershopSale.objects.filter(
        barbershop=user
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    # Staff stats
    active_staff = BarbershopStaff.objects.filter(
        barbershop=user,
        status='Active'
    ).count()
    
    # Customer stats
    total_customers = BarbershopCustomer.objects.filter(
        barbershop=user
    ).count()
    
    # Inventory stats
    low_stock_items = BarbershopInventory.objects.filter(
        barbershop=user,
        quantity__lte=F('min_stock')
    ).count()
    
    stats = {
        'today_appointments': today_appointments,
        'pending_appointments': pending_appointments,
        'completed_appointments': completed_appointments,
        'cancelled_appointments': cancelled_appointments,
        'today_sales': today_sales,
        'total_sales': total_sales,
        'active_staff': active_staff,
        'total_customers': total_customers,
        'low_stock_items': low_stock_items
    }
    
    serializer = DashboardStatsSerializer(stats)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsBarbershop])
def monthly_revenue(request):
    """Get monthly revenue data for charts"""
    user = request.user
    
    # Get last 12 months data
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=365)
    
    monthly_data = []
    for i in range(12):
        month_start = (start_date.replace(day=1) + timedelta(days=32*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        revenue = BarbershopSale.objects.filter(
            barbershop=user,
            sale_date__range=[month_start, month_end]
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        appointments = BarbershopAppointment.objects.filter(
            barbershop=user,
            appointment_date__range=[month_start, month_end],
            status='completed'
        ).count()
        
        monthly_data.append({
            'month': f"{calendar.month_name[month_start.month]} {month_start.year}",
            'revenue': revenue,
            'appointments': appointments
        })
    
    serializer = MonthlyRevenueSerializer(monthly_data, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsBarbershop])
def service_popularity(request):
    """Get service popularity data"""
    user = request.user
    
    services = BarbershopSale.objects.filter(
        barbershop=user
    ).values('service').annotate(
        count=Count('id'),
        revenue=Sum('amount')
    ).order_by('-count')
    
    serializer = ServicePopularitySerializer(services, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsBarbershop])
def staff_performance(request):
    """Get staff performance data"""
    user = request.user
    
    staff_data = BarbershopSale.objects.filter(
        barbershop=user
    ).values('barber_name').annotate(
        total_services=Count('id'),
        total_revenue=Sum('amount')
    ).order_by('-total_revenue')
    
    # Add staff names for better display
    for item in staff_data:
        item['staff_name'] = item['barber_name']
    
    serializer = StaffPerformanceSerializer(staff_data, many=True)
    return Response(serializer.data)


# Appointment Views
class AppointmentListCreateView(generics.ListCreateAPIView):
    """List and create appointments"""
    permission_classes = [IsBarbershop]
    pagination_class = PageNumberPagination
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BarbershopAppointmentListSerializer
        return BarbershopAppointmentSerializer
    
    def get_queryset(self):
        queryset = BarbershopAppointment.objects.filter(barbershop=self.request.user)
        
        # Filter by date if provided
        date = self.request.query_params.get('date')
        if date:
            queryset = queryset.filter(appointment_date=date)
        
        # Filter by status if provided
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by barber if provided
        barber = self.request.query_params.get('barber')
        if barber:
            queryset = queryset.filter(barber_name__icontains=barber)
        
        return queryset.order_by('-appointment_date', '-appointment_time')
    
    def perform_create(self, serializer):
        appointment = serializer.save(barbershop=self.request.user)
        
        # Create activity log
        BarbershopActivityLog.objects.create(
            barbershop=self.request.user,
            action_type='appointment_created',
            description=f"New appointment: {appointment.service} for {appointment.customer_name} on {appointment.appointment_date} at {appointment.appointment_time}",
            appointment=appointment
        )


class AppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete appointment"""
    serializer_class = BarbershopAppointmentSerializer
    permission_classes = [CanAccessOwnBarbershopData]
    
    def get_queryset(self):
        return BarbershopAppointment.objects.filter(barbershop=self.request.user)


@api_view(['GET'])
@permission_classes([IsBarbershop])
def today_appointments(request):
    """Get today's appointments"""
    user = request.user
    today = timezone.now().date()
    
    appointments = BarbershopAppointment.objects.filter(
        barbershop=user,
        appointment_date=today
    ).order_by('appointment_time')
    
    serializer = BarbershopAppointmentListSerializer(appointments, many=True)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsBarbershop])
def update_appointment_status(request, appointment_id):
    """Update appointment status"""
    try:
        appointment = BarbershopAppointment.objects.get(
            id=appointment_id,
            barbershop=request.user
        )
        
        new_status = request.data.get('status')
        if new_status not in ['confirmed', 'pending', 'cancelled', 'completed', 'no_show']:
            return Response(
                {'error': 'Invalid status'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        appointment.status = new_status
        appointment.save()
        
        # Create activity log
        BarbershopActivityLog.objects.create(
            barbershop=request.user,
            action_type='appointment_updated',
            description=f"Appointment status changed to {new_status}",
            appointment=appointment
        )
        
        serializer = BarbershopAppointmentSerializer(appointment)
        return Response(serializer.data)
        
    except BarbershopAppointment.DoesNotExist:
        return Response(
            {'error': 'Appointment not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


# Sales Views
class SaleListCreateView(generics.ListCreateAPIView):
    """List and create sales"""
    permission_classes = [IsBarbershop]
    pagination_class = PageNumberPagination
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BarbershopSaleListSerializer
        return BarbershopSaleSerializer
    
    def get_queryset(self):
        queryset = BarbershopSale.objects.filter(barbershop=self.request.user)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(sale_date__range=[start_date, end_date])
        
        # Filter by payment method
        payment_method = self.request.query_params.get('payment_method')
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)
        
        # Filter by service
        service = self.request.query_params.get('service')
        if service:
            queryset = queryset.filter(service=service)
        
        return queryset.order_by('-sale_date', '-created_at')
    
    def perform_create(self, serializer):
        sale = serializer.save(barbershop=self.request.user)
        
        # Create activity log
        BarbershopActivityLog.objects.create(
            barbershop=self.request.user,
            action_type='sale_recorded',
            description=f"Sale recorded: ₹{sale.amount} for {sale.service} by {sale.barber_name}",
            sale=sale
        )


class SaleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete sale"""
    serializer_class = BarbershopSaleSerializer
    permission_classes = [CanAccessOwnBarbershopData]
    
    def get_queryset(self):
        return BarbershopSale.objects.filter(barbershop=self.request.user)


@api_view(['GET'])
@permission_classes([IsBarbershop])
def daily_sales_summary(request):
    """Get daily sales summary"""
    user = request.user
    date = request.query_params.get('date', timezone.now().date())
    
    sales = BarbershopSale.objects.filter(
        barbershop=user,
        sale_date=date
    )
    
    summary = {
        'total_sales': sales.aggregate(total=Sum('amount'))['total'] or Decimal('0'),
        'total_transactions': sales.count(),
        'payment_breakdown': sales.values('payment_method').annotate(
            count=Count('id'),
            amount=Sum('amount')
        ),
        'service_breakdown': sales.values('service').annotate(
            count=Count('id'),
            amount=Sum('amount')
        )
    }
    
    return Response(summary)


# Staff Views
class StaffListCreateView(generics.ListCreateAPIView):
    """List and create staff"""
    permission_classes = [IsBarbershop]
    pagination_class = PageNumberPagination
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BarbershopStaffListSerializer
        return BarbershopStaffSerializer
    
    def get_queryset(self):
        queryset = BarbershopStaff.objects.filter(barbershop=self.request.user)
        
        # Filter by status
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by role
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        return queryset.order_by('name')
    
    def perform_create(self, serializer):
        staff = serializer.save(barbershop=self.request.user)
        
        # Create activity log
        BarbershopActivityLog.objects.create(
            barbershop=self.request.user,
            action_type='staff_added',
            description=f"New staff member added: {staff.name} - {staff.role}",
            staff=staff
        )


class StaffDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete staff"""
    serializer_class = BarbershopStaffSerializer
    permission_classes = [CanAccessOwnBarbershopData]
    
    def get_queryset(self):
        return BarbershopStaff.objects.filter(barbershop=self.request.user)


@api_view(['GET'])
@permission_classes([IsBarbershop])
def active_barbers(request):
    """Get active barbers for appointment booking"""
    user = request.user
    
    barbers = BarbershopStaff.objects.filter(
        barbershop=user,
        status='Active',
        role__in=['Barber', 'Senior Barber']
    ).values('name', 'role')
    
    return Response(list(barbers))


# Customer Views
class CustomerListCreateView(generics.ListCreateAPIView):
    """List and create customers"""
    permission_classes = [IsBarbershop]
    pagination_class = PageNumberPagination
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BarbershopCustomerListSerializer
        return BarbershopCustomerSerializer
    
    def get_queryset(self):
        queryset = BarbershopCustomer.objects.filter(barbershop=self.request.user)
        
        # Search by name or phone
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(phone__icontains=search)
            )
        
        return queryset.order_by('-last_visit_date', 'name')
    
    def perform_create(self, serializer):
        customer = serializer.save(barbershop=self.request.user)
        
        # Create activity log
        BarbershopActivityLog.objects.create(
            barbershop=self.request.user,
            action_type='customer_added',
            description=f"New customer added: {customer.name} - {customer.phone}",
            customer=customer
        )


class CustomerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete customer"""
    serializer_class = BarbershopCustomerSerializer
    permission_classes = [CanAccessOwnBarbershopData]
    
    def get_queryset(self):
        return BarbershopCustomer.objects.filter(barbershop=self.request.user)


@api_view(['POST'])
@permission_classes([IsBarbershop])
def update_customer_stats(request, customer_id):
    """Update customer visit statistics"""
    try:
        customer = BarbershopCustomer.objects.get(
            id=customer_id,
            barbershop=request.user
        )
        customer.update_visit_stats()
        
        serializer = BarbershopCustomerSerializer(customer)
        return Response(serializer.data)
        
    except BarbershopCustomer.DoesNotExist:
        return Response(
            {'error': 'Customer not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


# Inventory Views
class InventoryListCreateView(generics.ListCreateAPIView):
    """List and create inventory items"""
    permission_classes = [IsBarbershop]
    pagination_class = PageNumberPagination
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BarbershopInventoryListSerializer
        return BarbershopInventorySerializer
    
    def get_queryset(self):
        queryset = BarbershopInventory.objects.filter(barbershop=self.request.user)
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter by stock status
        stock_status = self.request.query_params.get('stock_status')
        if stock_status == 'low_stock':
            queryset = queryset.filter(quantity__lte=F('min_stock'))
        elif stock_status == 'out_of_stock':
            queryset = queryset.filter(quantity=0)
        
        return queryset.order_by('category', 'name')
    
    def perform_create(self, serializer):
        inventory = serializer.save(barbershop=self.request.user)
        
        # Create activity log
        BarbershopActivityLog.objects.create(
            barbershop=self.request.user,
            action_type='inventory_added',
            description=f"New inventory item: {inventory.name} - {inventory.category} (Qty: {inventory.quantity})",
            inventory=inventory
        )


class InventoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete inventory item"""
    serializer_class = BarbershopInventorySerializer
    permission_classes = [CanAccessOwnBarbershopData]
    
    def get_queryset(self):
        return BarbershopInventory.objects.filter(barbershop=self.request.user)


@api_view(['GET'])
@permission_classes([IsBarbershop])
def low_stock_alerts(request):
    """Get low stock items"""
    user = request.user
    
    low_stock_items = BarbershopInventory.objects.filter(
        barbershop=user,
        quantity__lte=F('min_stock')
    )
    
    serializer = BarbershopInventoryListSerializer(low_stock_items, many=True)
    return Response(serializer.data)


# Service Views
class ServiceListCreateView(generics.ListCreateAPIView):
    """List and create services"""
    permission_classes = [IsBarbershop]
    pagination_class = None  # Disable pagination for services
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BarbershopServiceListSerializer
        return BarbershopServiceSerializer
    
    def get_queryset(self):
        queryset = BarbershopService.objects.filter(barbershop=self.request.user)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active_bool)
        
        return queryset.order_by('name')
    
    def list(self, request, *args, **kwargs):
        """Override list to return custom response format"""
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            
            return Response({
                'success': True,
                'message': 'Services retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Failed to retrieve services: {str(e)}',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request, *args, **kwargs):
        """Override create to return custom response format"""
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                service = serializer.save(barbershop=request.user)
                
                # Create activity log
                BarbershopActivityLog.objects.create(
                    barbershop=request.user,
                    action_type='service_added',
                    description=f"New service added: {service.name} - ₹{service.price}"
                )
                
                return Response({
                    'success': True,
                    'message': 'Service created successfully',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Failed to create service: {str(e)}',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete service"""
    serializer_class = BarbershopServiceSerializer
    permission_classes = [CanAccessOwnBarbershopData]
    
    def get_queryset(self):
        return BarbershopService.objects.filter(barbershop=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to return custom response format"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            
            return Response({
                'success': True,
                'message': 'Service retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Failed to retrieve service: {str(e)}',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, *args, **kwargs):
        """Override update to return custom response format"""
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            
            if serializer.is_valid():
                service = serializer.save()
                
                # Create activity log
                BarbershopActivityLog.objects.create(
                    barbershop=request.user,
                    action_type='service_updated',
                    description=f"Service updated: {service.name} - ₹{service.price}"
                )
                
                return Response({
                    'success': True,
                    'message': 'Service updated successfully',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Failed to update service: {str(e)}',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, *args, **kwargs):
        """Override destroy to return custom response format"""
        try:
            instance = self.get_object()
            service_name = instance.name
            
            # Create activity log before deletion
            BarbershopActivityLog.objects.create(
                barbershop=request.user,
                action_type='service_deleted',
                description=f"Service deleted: {service_name}"
            )
            
            instance.delete()
            
            return Response({
                'success': True,
                'message': 'Service deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Failed to delete service: {str(e)}',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsBarbershop])
def active_services(request):
    """Get active services for dropdowns"""
    try:
        user = request.user
        
        services = BarbershopService.objects.filter(
            barbershop=user,
            is_active=True
        ).values('id', 'name', 'price')
        
        return Response({
            'success': True,
            'message': 'Active services retrieved successfully',
            'data': list(services)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to retrieve active services: {str(e)}',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Activity Log Views
class ActivityLogListView(generics.ListAPIView):
    """List activity logs"""
    serializer_class = BarbershopActivityLogSerializer
    permission_classes = [IsBarbershop]
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        queryset = BarbershopActivityLog.objects.filter(barbershop=self.request.user)
        
        # Filter by action type
        action_type = self.request.query_params.get('action_type')
        if action_type:
            queryset = queryset.filter(action_type=action_type)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        
        return queryset.order_by('-created_at')[:100]  # Limit to last 100 entries


# Reports Views
@api_view(['GET'])
@permission_classes([IsBarbershop])
def reports_summary(request):
    """Get comprehensive reports summary"""
    user = request.user
    
    # Date range from query params
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    
    if not start_date or not end_date:
        # Default to current month
        today = timezone.now().date()
        start_date = today.replace(day=1)
        end_date = today
    
    # Revenue summary
    revenue_data = BarbershopSale.objects.filter(
        barbershop=user,
        sale_date__range=[start_date, end_date]
    ).aggregate(
        total_revenue=Sum('amount'),
        total_transactions=Count('id'),
        avg_transaction=Avg('amount')
    )
    
    # Appointment summary
    appointment_data = BarbershopAppointment.objects.filter(
        barbershop=user,
        appointment_date__range=[start_date, end_date]
    ).aggregate(
        total_appointments=Count('id'),
        completed_appointments=Count('id', filter=Q(status='completed')),
        cancelled_appointments=Count('id', filter=Q(status='cancelled'))
    )
    
    # Service breakdown
    service_data = BarbershopSale.objects.filter(
        barbershop=user,
        sale_date__range=[start_date, end_date]
    ).values('service').annotate(
        count=Count('id'),
        revenue=Sum('amount')
    ).order_by('-revenue')
    
    # Staff performance
    staff_data = BarbershopSale.objects.filter(
        barbershop=user,
        sale_date__range=[start_date, end_date]
    ).values('barber_name').annotate(
        services_count=Count('id'),
        revenue=Sum('amount')
    ).order_by('-revenue')
    
    summary = {
        'date_range': {'start': start_date, 'end': end_date},
        'revenue': revenue_data,
        'appointments': appointment_data,
        'services': service_data,
        'staff_performance': staff_data
    }
    
    return Response(summary)


# Additional Views for Calendar and Scheduling
@api_view(['GET'])
@permission_classes([IsBarbershop])
def calendar_view(request):
    """Get calendar view data with appointments"""
    user = request.user
    
    # Get month and year from query params
    month = int(request.query_params.get('month', timezone.now().month))
    year = int(request.query_params.get('year', timezone.now().year))
    
    # Get all appointments for the month
    start_date = datetime(year, month, 1).date()
    if month == 12:
        end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
    
    appointments = BarbershopAppointment.objects.filter(
        barbershop=user,
        appointment_date__range=[start_date, end_date]
    ).order_by('appointment_date', 'appointment_time')
    
    # Group appointments by date
    calendar_data = {}
    for appointment in appointments:
        date_str = appointment.appointment_date.strftime('%Y-%m-%d')
        if date_str not in calendar_data:
            calendar_data[date_str] = []
        
        calendar_data[date_str].append({
            'id': appointment.id,
            'customer_name': appointment.customer_name,
            'service': appointment.service,
            'time': appointment.appointment_time.strftime('%H:%M'),
            'status': appointment.status,
            'barber': appointment.barber_name
        })
    
    return Response({
        'month': month,
        'year': year,
        'appointments': calendar_data
    })


@api_view(['GET'])
@permission_classes([IsBarbershop])
def schedule_grid(request):
    """Get schedule grid for a specific date"""
    user = request.user
    date = request.query_params.get('date', timezone.now().date())
    
    # Convert string to date if needed
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d').date()
    
    # Get all appointments for the date
    appointments = BarbershopAppointment.objects.filter(
        barbershop=user,
        appointment_date=date
    ).order_by('appointment_time')
    
    # Get active staff
    staff = BarbershopStaff.objects.filter(
        barbershop=user,
        status='Active'
    ).values('name', 'role')
    
    # Time slots (9 AM to 8 PM, 30-minute intervals)
    time_slots = []
    start_time = datetime.strptime('09:00', '%H:%M').time()
    end_time = datetime.strptime('20:00', '%H:%M').time()
    
    current_time = datetime.combine(date, start_time)
    end_datetime = datetime.combine(date, end_time)
    
    while current_time <= end_datetime:
        time_slots.append(current_time.strftime('%H:%M'))
        current_time += timedelta(minutes=30)
    
    # Build schedule grid
    schedule_grid = {
        'date': date.strftime('%Y-%m-%d'),
        'staff': list(staff),
        'time_slots': time_slots,
        'appointments': []
    }
    
    for appointment in appointments:
        schedule_grid['appointments'].append({
            'id': appointment.id,
            'time': appointment.appointment_time.strftime('%H:%M'),
            'customer': appointment.customer_name,
            'service': appointment.service,
            'barber': appointment.barber_name,
            'status': appointment.status,
            'duration': appointment.duration_minutes or 30
        })
    
    return Response(schedule_grid)


@api_view(['GET'])
@permission_classes([IsBarbershop])
def available_time_slots(request):
    """Get available time slots for a specific date and barber"""
    user = request.user
    date = request.query_params.get('date')
    barber_name = request.query_params.get('barber')
    
    if not date:
        return Response({'error': 'Date is required'}, status=400)
    
    # Convert string to date
    try:
        appointment_date = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return Response({'error': 'Invalid date format'}, status=400)
    
    # Get existing appointments for the date and barber
    existing_appointments = BarbershopAppointment.objects.filter(
        barbershop=user,
        appointment_date=appointment_date,
        status__in=['confirmed', 'pending']
    )
    
    if barber_name:
        existing_appointments = existing_appointments.filter(barber_name=barber_name)
    
    # Generate time slots (9 AM to 8 PM, 30-minute intervals)
    time_slots = []
    start_time = datetime.strptime('09:00', '%H:%M').time()
    end_time = datetime.strptime('20:00', '%H:%M').time()
    
    current_time = datetime.combine(appointment_date, start_time)
    end_datetime = datetime.combine(appointment_date, end_time)
    
    while current_time <= end_datetime:
        time_slot = current_time.strftime('%H:%M')
        
        # Check if slot is available
        is_available = not existing_appointments.filter(
            appointment_time=current_time.time()
        ).exists()
        
        time_slots.append({
            'time': time_slot,
            'available': is_available
        })
        
        current_time += timedelta(minutes=30)
    
    return Response({
        'date': date,
        'barber': barber_name,
        'time_slots': time_slots
    })


@api_view(['POST'])
@permission_classes([IsBarbershop])
def block_time_slot(request):
    """Block a time slot for maintenance or break"""
    user = request.user
    
    data = request.data
    date = data.get('date')
    time = data.get('time')
    barber_name = data.get('barber_name')
    reason = data.get('reason', 'Blocked')
    
    try:
        appointment_date = datetime.strptime(date, '%Y-%m-%d').date()
        appointment_time = datetime.strptime(time, '%H:%M').time()
        
        # Create a blocked appointment
        blocked_appointment = BarbershopAppointment.objects.create(
            barbershop=user,
            customer_name='BLOCKED',
            customer_phone='',
            service=reason,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            barber_name=barber_name,
            status='confirmed',
            duration_minutes=30,
            notes=f'Time slot blocked: {reason}'
        )
        
        # Log activity
        BarbershopActivityLog.objects.create(
            barbershop=user,
            action_type='time_blocked',
            description=f'Time slot blocked: {date} {time} - {reason}',
            appointment=blocked_appointment
        )
        
        return Response({
            'success': True,
            'appointment_id': blocked_appointment.id,
            'message': 'Time slot blocked successfully'
        })
        
    except ValueError as e:
        return Response({'error': 'Invalid date or time format'}, status=400)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


# Analytics and Reports Views
@api_view(['GET'])
@permission_classes([IsBarbershop])
def business_analytics(request):
    """Get comprehensive business analytics"""
    user = request.user
    
    # Date range
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)  # Last 30 days
    
    # Revenue analytics
    daily_revenue = []
    for i in range(30):
        date = start_date + timedelta(days=i)
        revenue = BarbershopSale.objects.filter(
            barbershop=user,
            sale_date=date
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        daily_revenue.append({
            'date': date.strftime('%Y-%m-%d'),
            'revenue': revenue
        })
    
    # Service performance
    service_performance = BarbershopSale.objects.filter(
        barbershop=user,
        sale_date__range=[start_date, end_date]
    ).values('service').annotate(
        count=Count('id'),
        revenue=Sum('amount'),
        avg_price=Avg('amount')
    ).order_by('-revenue')
    
    # Customer retention
    total_customers = BarbershopCustomer.objects.filter(barbershop=user).count()
    returning_customers = BarbershopCustomer.objects.filter(
        barbershop=user,
        total_visits__gt=1
    ).count()
    
    retention_rate = (returning_customers / total_customers * 100) if total_customers > 0 else 0
    
    # Peak hours analysis
    peak_hours = BarbershopAppointment.objects.filter(
        barbershop=user,
        appointment_date__range=[start_date, end_date],
        status='completed'
    ).extra(
        select={'hour': 'EXTRACT(hour FROM appointment_time)'}
    ).values('hour').annotate(
        count=Count('id')
    ).order_by('-count')
    
    analytics = {
        'date_range': {
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d')
        },
        'daily_revenue': daily_revenue,
        'service_performance': list(service_performance),
        'customer_retention': {
            'total_customers': total_customers,
            'returning_customers': returning_customers,
            'retention_rate': round(retention_rate, 2)
        },
        'peak_hours': list(peak_hours)
    }
    
    return Response(analytics)


@api_view(['GET'])
@permission_classes([IsBarbershop])
def export_data(request):
    """Export data for external analysis"""
    user = request.user
    data_type = request.query_params.get('type', 'all')
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    
    # Default to last 30 days if no dates provided
    if not start_date or not end_date:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    export_data = {}
    
    if data_type in ['all', 'appointments']:
        appointments = BarbershopAppointment.objects.filter(
            barbershop=user,
            appointment_date__range=[start_date, end_date]
        ).values(
            'id', 'customer_name', 'customer_phone', 'service',
            'appointment_date', 'appointment_time', 'barber_name',
            'status', 'duration_minutes', 'created_at'
        )
        export_data['appointments'] = list(appointments)
    
    if data_type in ['all', 'sales']:
        sales = BarbershopSale.objects.filter(
            barbershop=user,
            sale_date__range=[start_date, end_date]
        ).values(
            'id', 'customer_name', 'service', 'amount', 'payment_method',
            'sale_date', 'barber_name', 'created_at'
        )
        export_data['sales'] = list(sales)
    
    if data_type in ['all', 'customers']:
        customers = BarbershopCustomer.objects.filter(
            barbershop=user
        ).values(
            'id', 'name', 'phone', 'email', 'total_visits',
            'total_spent', 'last_visit_date', 'created_at'
        )
        export_data['customers'] = list(customers)
    
    if data_type in ['all', 'inventory']:
        inventory = BarbershopInventory.objects.filter(
            barbershop=user
        ).values(
            'id', 'name', 'category', 'quantity', 'unit', 'cost_per_unit',
            'selling_price', 'min_stock', 'supplier', 'last_restocked'
        )
        export_data['inventory'] = list(inventory)
    
    return Response({
        'export_date': timezone.now().isoformat(),
        'date_range': {
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d')
        },
        'data': export_data
    })


# Staff Availability Management
@api_view(['GET', 'POST'])
@permission_classes([IsBarbershop])
def staff_availability(request):
    """Manage staff availability schedules"""
    if request.method == 'GET':
        staff_name = request.query_params.get('staff_name')
        date = request.query_params.get('date')
        
        queryset = BarbershopStaffAvailability.objects.filter(
            staff__barbershop=request.user
        )
        
        if staff_name:
            queryset = queryset.filter(staff__name=staff_name)
        
        if date:
            queryset = queryset.filter(date=date)
        
        availability = queryset.order_by('date', 'start_time')
        serializer = BarbershopStaffAvailabilitySerializer(availability, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Create new availability entry or update existing one
        print(f"DEBUG: POST data received: {request.data}")
        print(f"DEBUG: User: {request.user} (ID: {request.user.id})")
        
        # Check if staff exists and belongs to this barbershop
        if 'staff' in request.data:
            try:
                staff = BarbershopStaff.objects.get(id=request.data['staff'], barbershop=request.user)
                print(f"DEBUG: Staff found: {staff.name} (ID: {staff.id}), Barbershop: {staff.barbershop}")
            except BarbershopStaff.DoesNotExist:
                print(f"DEBUG: Staff with ID {request.data['staff']} does not exist or doesn't belong to user's barbershop")
                return Response(
                    {"error": "Staff member not found or doesn't belong to your barbershop"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Check if a record already exists for this staff, date, and start_time
        existing_availability = None
        if all(key in request.data for key in ['staff', 'date', 'start_time']):
            existing_availability = BarbershopStaffAvailability.objects.filter(
                staff_id=request.data['staff'],
                date=request.data['date'],
                start_time=request.data['start_time']
            ).first()
        
        if existing_availability:
            print(f"DEBUG: Found existing availability record: {existing_availability}")
            print(f"DEBUG: Current is_available: {existing_availability.is_available}")
            print(f"DEBUG: New is_available: {request.data.get('is_available')}")
            serializer = BarbershopStaffAvailabilitySerializer(
                existing_availability, 
                data=request.data, 
                partial=True
            )
        else:
            print(f"DEBUG: No existing record found, creating new one")
            serializer = BarbershopStaffAvailabilitySerializer(data=request.data)
        
        if serializer.is_valid():
            updated_record = serializer.save()
            status_code = status.HTTP_200_OK if existing_availability else status.HTTP_201_CREATED
            print(f"DEBUG: Successfully {'updated' if existing_availability else 'created'} availability record")
            print(f"DEBUG: Final record is_available: {updated_record.is_available}")
            return Response(serializer.data, status=status_code)
        
        print(f"DEBUG: Serializer validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsBarbershop])
def staff_availability_detail(request, pk):
    """Retrieve, update or delete a specific staff availability record"""
    try:
        availability = BarbershopStaffAvailability.objects.get(
            pk=pk, 
            staff__barbershop=request.user
        )
    except BarbershopStaffAvailability.DoesNotExist:
        return Response(
            {"error": "Staff availability record not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = BarbershopStaffAvailabilitySerializer(availability)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = BarbershopStaffAvailabilitySerializer(
            availability, 
            data=request.data, 
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        availability.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Quick Actions
@api_view(['POST'])
@permission_classes([IsBarbershop])
def quick_appointment(request):
    """Create a quick walk-in appointment"""
    user = request.user
    
    # Get current time
    now = timezone.now()
    appointment_data = {
        'barbershop': user.id,
        'customer_name': request.data.get('customer_name', 'Walk-in'),
        'customer_phone': request.data.get('customer_phone', ''),
        'service': request.data.get('service'),
        'appointment_date': now.date(),
        'appointment_time': now.time(),
        'barber_name': request.data.get('barber_name'),
        'status': 'confirmed',
        'notes': 'Walk-in appointment'
    }
    
    serializer = BarbershopAppointmentSerializer(data=appointment_data)
    if serializer.is_valid():
        appointment = serializer.save()
        
        # Log activity
        BarbershopActivityLog.objects.create(
            barbershop=user,
            action_type='walk_in_appointment',
            description=f'Walk-in appointment created for {appointment.customer_name}',
            appointment=appointment
        )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsBarbershop])
def quick_sale(request):
    """Record a quick sale"""
    user = request.user
    
    sale_data = {
        'barbershop': user.id,
        'customer_name': request.data.get('customer_name', 'Walk-in'),
        'service': request.data.get('service'),
        'amount': request.data.get('amount'),
        'payment_method': request.data.get('payment_method', 'Cash'),
        'sale_date': timezone.now().date(),
        'barber_name': request.data.get('barber_name')
    }
    
    serializer = BarbershopSaleSerializer(data=sale_data)
    if serializer.is_valid():
        sale = serializer.save()
        
        # Update customer record if exists
        try:
            customer = BarbershopCustomer.objects.get(
                barbershop=user,
                name=sale.customer_name
            )
            customer.update_visit_stats()
        except BarbershopCustomer.DoesNotExist:
            pass
        
        # Log activity
        BarbershopActivityLog.objects.create(
            barbershop=user,
            action_type='quick_sale',
            description=f'Quick sale recorded: {sale.service} - ${sale.amount}',
            sale=sale
        )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
