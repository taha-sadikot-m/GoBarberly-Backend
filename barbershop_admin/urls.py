"""
URL configuration for Admin functionality
"""
from django.urls import path
from . import views

app_name = 'barbershop_admin'

urlpatterns = [
    # Dashboard endpoints
    path('dashboard/stats/', views.admin_dashboard_stats, name='admin_dashboard_stats'),
    path('dashboard/data/', views.admin_dashboard_data, name='admin_dashboard_data'),
    
    # Activity endpoints
    path('activities/', views.ActivityListView.as_view(), name='admin_activities'),
    
    # Appointment endpoints
    path('appointments/', views.AppointmentListCreateView.as_view(), name='admin_appointments'),
    path('appointments/<int:pk>/', views.AppointmentDetailView.as_view(), name='admin_appointment_detail'),
    
    # Barbershop management endpoints
    path('barbershops/', views.AdminBarbershopListCreateView.as_view(), name='admin_barbershops'),
    path('barbershops/<int:pk>/', views.AdminBarbershopDetailView.as_view(), name='admin_barbershop_detail'),
    path('barbershops/<int:barbershop_id>/toggle-status/', views.toggle_barbershop_status, name='admin_toggle_barbershop_status'),
    path('barbershops/<int:barbershop_id>/analytics/', views.admin_barbershop_analytics, name='admin_barbershop_analytics'),
    
    # Archive endpoints - NEW
    path('archive/barbershops/', views.ArchivedBarbershopListView.as_view(), name='archived_barbershops'),
    path('archive/restore/', views.RestoreBarbershopView.as_view(), name='restore_barbershop'),
    
    # Transfer endpoints - NEW
    path('transfer/barbershop/', views.TransferBarbershopOwnershipView.as_view(), name='transfer_barbershop'),
    path('transfer/available-admins/', views.AvailableAdminsForTransferView.as_view(), name='available_admins'),
]