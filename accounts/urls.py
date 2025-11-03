from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication endpoints
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.CustomTokenObtainPairView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Email verification endpoints
    path('verify-email/', views.EmailVerificationView.as_view(), name='verify_email'),
    path('resend-verification/', views.ResendVerificationView.as_view(), name='resend_verification'),
    
    # Password management endpoints
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('forgot-password/', views.PasswordResetRequestView.as_view(), name='forgot_password'),
    path('reset-password/', views.PasswordResetConfirmView.as_view(), name='reset_password'),
    
    # User profile endpoints
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    
    # Admin endpoints
    path('users/', views.UserListView.as_view(), name='user_list'),
]