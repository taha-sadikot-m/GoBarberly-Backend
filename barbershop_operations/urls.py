"""
URL configuration for Barbershop Operations
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'barbershop_operations'

urlpatterns = [
    # Profile URLs
    path('profile/', views.BarbershopProfileView.as_view(), name='barbershop_profile'),
    
    # Dashboard URLs
    path('dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),
    path('dashboard/monthly-revenue/', views.monthly_revenue, name='monthly_revenue'),
    path('dashboard/service-popularity/', views.service_popularity, name='service_popularity'),
    path('dashboard/staff-performance/', views.staff_performance, name='staff_performance'),
    
    # Appointment URLs
    path('appointments/', views.AppointmentListCreateView.as_view(), name='appointment_list_create'),
    path('appointments/<uuid:pk>/', views.AppointmentDetailView.as_view(), name='appointment_detail'),
    path('appointments/today/', views.today_appointments, name='today_appointments'),
    path('appointments/<uuid:appointment_id>/status/', views.update_appointment_status, name='update_appointment_status'),
    
    # Sales URLs
    path('sales/', views.SaleListCreateView.as_view(), name='sale_list_create'),
    path('sales/<int:pk>/', views.SaleDetailView.as_view(), name='sale_detail'),
    path('sales/daily-summary/', views.daily_sales_summary, name='daily_sales_summary'),
    
    # Staff URLs
    path('staff/', views.StaffListCreateView.as_view(), name='staff_list_create'),
    path('staff/<int:pk>/', views.StaffDetailView.as_view(), name='staff_detail'),
    path('staff/active-barbers/', views.active_barbers, name='active_barbers'),
    path('staff/availability/', views.staff_availability, name='staff_availability'),
    path('staff/availability/<int:pk>/', views.staff_availability_detail, name='staff_availability_detail'),
    
    # Customer URLs
    path('customers/', views.CustomerListCreateView.as_view(), name='customer_list_create'),
    path('customers/<int:pk>/', views.CustomerDetailView.as_view(), name='customer_detail'),
    path('customers/<int:customer_id>/update-stats/', views.update_customer_stats, name='update_customer_stats'),
    
    # Inventory URLs
    path('inventory/', views.InventoryListCreateView.as_view(), name='inventory_list_create'),
    path('inventory/<int:pk>/', views.InventoryDetailView.as_view(), name='inventory_detail'),
    path('inventory/low-stock/', views.low_stock_alerts, name='low_stock_alerts'),
    
    # Service URLs
    path('services/', views.ServiceListCreateView.as_view(), name='service_list_create'),
    path('services/<int:pk>/', views.ServiceDetailView.as_view(), name='service_detail'),
    path('services/active/', views.active_services, name='active_services'),
    
    # Activity Log URLs
    path('activity-logs/', views.ActivityLogListView.as_view(), name='activity_log_list'),
    
    # Reports URLs
    path('reports/summary/', views.reports_summary, name='reports_summary'),
    path('reports/analytics/', views.business_analytics, name='business_analytics'),
    path('reports/export/', views.export_data, name='export_data'),
    
    # Calendar and Scheduling URLs
    path('calendar/', views.calendar_view, name='calendar_view'),
    path('schedule/grid/', views.schedule_grid, name='schedule_grid'),
    path('schedule/available-slots/', views.available_time_slots, name='available_time_slots'),
    path('schedule/block-slot/', views.block_time_slot, name='block_time_slot'),
    
    # Quick Actions URLs
    path('quick/appointment/', views.quick_appointment, name='quick_appointment'),
    path('quick/sale/', views.quick_sale, name='quick_sale'),
]