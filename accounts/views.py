from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema, OpenApiResponse
import logging

from .models import User, EmailVerificationToken, PasswordResetToken, UserLoginHistory
from .serializers import (
    UserRegistrationSerializer,
    CustomTokenObtainPairSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    EmailVerificationSerializer,
    ResendVerificationSerializer,
    UserListSerializer,
)
from .utils import send_verification_email, send_password_reset_email, get_client_ip, get_user_agent

logger = logging.getLogger(__name__)

User = get_user_model()


def create_response(success=True, message="", data=None, errors=None, status_code=status.HTTP_200_OK):
    """
    Create standardized API response
    """
    return Response({
        "success": success,
        "message": message,
        "data": data,
        "errors": errors
    }, status=status_code)


@extend_schema(
    tags=['Authentication'],
    summary='User Registration',
    description='Register a new user account with email verification',
)
class UserRegistrationView(generics.CreateAPIView):
    """
    API view for user registration
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        """
        Register a new user
        """
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                
                # Send verification email
                try:
                    send_verification_email(user, request)
                    logger.info(f"Verification email sent to {user.email}")
                except Exception as e:
                    logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
                
                # Log registration
                UserLoginHistory.objects.create(
                    user=user,
                    email=user.email,
                    ip_address=get_client_ip(request),
                    user_agent=get_user_agent(request),
                    status='success'
                )
                
                return create_response(
                    success=True,
                    message="Registration successful. Please check your email for verification link.",
                    data={
                        "user_id": user.id,
                        "email": user.email,
                        "username": user.username
                    },
                    status_code=status.HTTP_201_CREATED
                )
            
            return create_response(
                success=False,
                message="Registration failed. Please check the provided information.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return create_response(
                success=False,
                message="An error occurred during registration. Please try again.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(
    tags=['Authentication'],
    summary='User Login',
    description='Authenticate user and return JWT tokens',
)
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token obtain view with additional response data
    """
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        """
        Authenticate user and return tokens
        """
        try:
            serializer = self.get_serializer(data=request.data)
            
            if serializer.is_valid():
                # Log successful login
                user = serializer.user
                UserLoginHistory.objects.create(
                    user=user,
                    email=user.email,
                    ip_address=get_client_ip(request),
                    user_agent=get_user_agent(request),
                    status='success'
                )
                
                # Update last login IP
                user.last_login_ip = get_client_ip(request)
                user.save(update_fields=['last_login_ip'])
                
                return create_response(
                    success=True,
                    message="Login successful",
                    data=serializer.validated_data,
                    status_code=status.HTTP_200_OK
                )
            
            # Log failed login attempt
            email = request.data.get('email', '')
            UserLoginHistory.objects.create(
                email=email,
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request),
                status='failed',
                failure_reason='Invalid credentials'
            )
            
            return create_response(
                success=False,
                message="Invalid credentials",
                errors=serializer.errors,
                status_code=status.HTTP_401_UNAUTHORIZED
            )
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return create_response(
                success=False,
                message="An error occurred during login. Please try again.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(
    tags=['Authentication'],
    summary='User Logout',
    description='Logout user and blacklist refresh token',
)
class LogoutView(APIView):
    """
    API view for user logout
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Logout user by blacklisting refresh token
        """
        try:
            refresh_token = request.data.get("refresh_token")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return create_response(
                success=True,
                message="Successfully logged out",
                status_code=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return create_response(
                success=False,
                message="An error occurred during logout",
                status_code=status.HTTP_400_BAD_REQUEST
            )


@extend_schema(
    tags=['User Profile'],
    summary='Get User Profile',
    description='Get current user profile information',
)
class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API view for user profile management
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def retrieve(self, request, *args, **kwargs):
        """
        Get user profile
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            
            return create_response(
                success=True,
                message="Profile retrieved successfully",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Profile retrieval error: {str(e)}")
            return create_response(
                success=False,
                message="Failed to retrieve profile",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def update(self, request, *args, **kwargs):
        """
        Update user profile
        """
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            
            if serializer.is_valid():
                serializer.save()
                
                return create_response(
                    success=True,
                    message="Profile updated successfully",
                    data=serializer.data,
                    status_code=status.HTTP_200_OK
                )
            
            return create_response(
                success=False,
                message="Profile update failed",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            logger.error(f"Profile update error: {str(e)}")
            return create_response(
                success=False,
                message="Failed to update profile",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(
    tags=['Authentication'],
    summary='Change Password',
    description='Change user password',
)
class ChangePasswordView(APIView):
    """
    API view for changing password
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Change user password
        """
        try:
            serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
            
            if serializer.is_valid():
                user = request.user
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                
                logger.info(f"Password changed for user {user.email}")
                
                return create_response(
                    success=True,
                    message="Password changed successfully",
                    status_code=status.HTTP_200_OK
                )
            
            return create_response(
                success=False,
                message="Password change failed",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            logger.error(f"Password change error: {str(e)}")
            return create_response(
                success=False,
                message="Failed to change password",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(
    tags=['Authentication'],
    summary='Request Password Reset',
    description='Request password reset email',
)
class PasswordResetRequestView(APIView):
    """
    API view for password reset request
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """
        Send password reset email
        """
        try:
            serializer = PasswordResetRequestSerializer(data=request.data)
            
            if serializer.is_valid():
                email = serializer.validated_data['email']
                
                try:
                    user = User.objects.get(email=email)
                    send_password_reset_email(user, request)
                    logger.info(f"Password reset email sent to {email}")
                except User.DoesNotExist:
                    # Don't reveal if email exists or not
                    logger.warning(f"Password reset requested for non-existent email: {email}")
                
                return create_response(
                    success=True,
                    message="If the email exists in our system, you will receive a password reset link.",
                    status_code=status.HTTP_200_OK
                )
            
            return create_response(
                success=False,
                message="Invalid email format",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            logger.error(f"Password reset request error: {str(e)}")
            return create_response(
                success=False,
                message="Failed to process password reset request",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(
    tags=['Authentication'],
    summary='Reset Password',
    description='Reset password using token',
)
class PasswordResetConfirmView(APIView):
    """
    API view for password reset confirmation
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """
        Reset password with token
        """
        try:
            serializer = PasswordResetConfirmSerializer(data=request.data)
            
            if serializer.is_valid():
                reset_token = serializer.reset_token
                new_password = serializer.validated_data['new_password']
                
                # Reset password
                user = reset_token.user
                user.set_password(new_password)
                user.save()
                
                # Mark token as used
                reset_token.is_used = True
                reset_token.save()
                
                logger.info(f"Password reset completed for user {user.email}")
                
                return create_response(
                    success=True,
                    message="Password reset successful",
                    status_code=status.HTTP_200_OK
                )
            
            return create_response(
                success=False,
                message="Password reset failed",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            logger.error(f"Password reset confirmation error: {str(e)}")
            return create_response(
                success=False,
                message="Failed to reset password",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(
    tags=['Authentication'],
    summary='Verify Email',
    description='Verify user email address',
)
class EmailVerificationView(APIView):
    """
    API view for email verification
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """
        Verify email with token from URL parameter (for email links)
        """
        try:
            token = request.GET.get('token')
            if not token:
                return create_response(
                    success=False,
                    message="Token parameter is required",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Use the same logic as POST method
            serializer = EmailVerificationSerializer(data={'token': token})
            
            if serializer.is_valid():
                verification_token = serializer.verification_token
                user = verification_token.user
                
                # Verify email
                user.is_email_verified = True
                user.save()
                
                # Mark token as used
                verification_token.is_used = True
                verification_token.save()
                
                logger.info(f"Email verified for user {user.email}")
                
                return create_response(
                    success=True,
                    message="Email verified successfully! You can now log in to your account.",
                    data={
                        "user_email": user.email,
                        "redirect_url": "/login"  # You can customize this
                    },
                    status_code=status.HTTP_200_OK
                )
            
            return create_response(
                success=False,
                message="Email verification failed",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            logger.error(f"Email verification error: {str(e)}")
            return create_response(
                success=False,
                message="Failed to verify email",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """
        Verify email with token in request body (for API calls)
        """
        try:
            serializer = EmailVerificationSerializer(data=request.data)
            
            if serializer.is_valid():
                verification_token = serializer.verification_token
                user = verification_token.user
                
                # Verify email
                user.is_email_verified = True
                user.save()
                
                # Mark token as used
                verification_token.is_used = True
                verification_token.save()
                
                logger.info(f"Email verified for user {user.email}")
                
                return create_response(
                    success=True,
                    message="Email verified successfully",
                    status_code=status.HTTP_200_OK
                )
            
            return create_response(
                success=False,
                message="Email verification failed",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            logger.error(f"Email verification error: {str(e)}")
            return create_response(
                success=False,
                message="Failed to verify email",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(
    tags=['Authentication'],
    summary='Resend Verification Email',
    description='Resend email verification link',
)
class ResendVerificationView(APIView):
    """
    API view for resending email verification
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """
        Resend verification email
        """
        try:
            serializer = ResendVerificationSerializer(data=request.data)
            
            if serializer.is_valid():
                user = serializer.user
                send_verification_email(user, request)
                
                logger.info(f"Verification email resent to {user.email}")
                
                return create_response(
                    success=True,
                    message="Verification email sent successfully",
                    status_code=status.HTTP_200_OK
                )
            
            return create_response(
                success=False,
                message="Failed to send verification email",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            logger.error(f"Resend verification error: {str(e)}")
            return create_response(
                success=False,
                message="Failed to resend verification email",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(
    tags=['Admin'],
    summary='List Users',
    description='Get list of all users (admin only)',
)
class UserListView(generics.ListAPIView):
    """
    API view for listing users (admin only)
    """
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Only allow admin users to list all users
        if self.request.user.is_admin_user:
            return User.objects.all().order_by('-created_at')
        return User.objects.none()
    
    def list(self, request, *args, **kwargs):
        """
        List all users
        """
        try:
            if not request.user.is_admin_user:
                return create_response(
                    success=False,
                    message="Permission denied. Admin access required.",
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)
            
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response({
                    "success": True,
                    "message": "Users retrieved successfully",
                    "data": serializer.data
                })
            
            serializer = self.get_serializer(queryset, many=True)
            return create_response(
                success=True,
                message="Users retrieved successfully",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"User list error: {str(e)}")
            return create_response(
                success=False,
                message="Failed to retrieve users",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
