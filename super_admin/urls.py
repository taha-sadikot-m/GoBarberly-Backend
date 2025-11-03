"""
URL configuration for super_admin app
"""
from django.urls import path
from . import views

app_name = 'super_admin'

urlpatterns = [
    # Dashboard endpoints
    path('dashboard/stats/', views.DashboardStatsView.as_view(), name='dashboard_stats'),
    path('dashboard/data/', views.load_dashboard_data, name='dashboard_data'),
    
    # Admin management endpoints
    path('admins/', views.AdminListCreateView.as_view(), name='admin_list_create'),
    path('admins/<int:pk>/', views.AdminDetailView.as_view(), name='admin_detail'),
    path('admins/<int:pk>/toggle-status/', views.AdminToggleStatusView.as_view(), name='admin_toggle_status'),
    path('admins/<int:pk>/transfer-ownership/', views.AdminTransferOwnershipView.as_view(), name='admin_transfer_ownership'),
    path('admins/<int:pk>/barbershops/', views.AdminBarbershopsView.as_view(), name='admin_barbershops'),
    
    # Barbershop management endpoints
    path('barbershops/', views.BarbershopListCreateView.as_view(), name='barbershop_list_create'),
    path('barbershops/<int:pk>/', views.BarbershopDetailView.as_view(), name='barbershop_detail'),
    path('barbershops/<int:pk>/toggle-status/', views.BarbershopToggleStatusView.as_view(), name='barbershop_toggle_status'),
    
    # Archive endpoints - NEW
    path('archive/admins/', views.ArchivedAdminListView.as_view(), name='archived_admins'),
    path('archive/barbershops/', views.ArchivedBarbershopListView.as_view(), name='archived_barbershops'),
    path('archive/restore/', views.RestoreUserView.as_view(), name='restore_user'),
]