from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import User, EmailVerificationToken, PasswordResetToken
import re


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name', 'last_name', 
            'phone_number', 'password', 'password_confirm', 'role'
        )
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate_email(self, value):
        """Validate email format and uniqueness"""
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()
    
    def validate_username(self, value):
        """Validate username format and uniqueness"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        
        # Username should be alphanumeric with underscores
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError(
                "Username can only contain letters, numbers, and underscores."
            )
        
        return value
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        if value and not re.match(r'^\+?1?\d{9,15}$', value):
            raise serializers.ValidationError(
                "Phone number must be in valid format (e.g., +1234567890)"
            )
        return value
    
    def validate_password(self, value):
        """Validate password using Django's password validators"""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    
    def validate(self, attrs):
        """Validate password confirmation"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': "Password confirmation doesn't match."
            })
        
        # Remove password_confirm from validated data
        attrs.pop('password_confirm')
        return attrs
    
    def create(self, validated_data):
        """Create new user with hashed password"""
        password = validated_data.pop('password')
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer with additional user information
    """
    username_field = 'email'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'] = serializers.EmailField()
        self.fields['password'] = serializers.CharField(style={'input_type': 'password'})
        # Remove username field since we're using email
        if 'username' in self.fields:
            del self.fields['username']
    
    def validate(self, attrs):
        """Validate credentials and return tokens with user data"""
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError(
                    'No active account found with the given credentials'
                )
            
            if not user.is_email_verified:
                raise serializers.ValidationError(
                    'Email address is not verified. Please verify your email first.'
                )
            
            # Update the username field with email for token generation
            attrs['username'] = email
        
        data = super().validate(attrs)
        
        # Add user information to the response
        data.update({
            'user': {
                'id': self.user.id,
                'email': self.user.email,
                'username': self.user.username,
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'role': self.user.role,
                'is_email_verified': self.user.is_email_verified,
                'is_profile_complete': self.user.is_profile_complete,
            }
        })
        
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile information
    """
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'full_name',
            'phone_number', 'date_of_birth', 'profile_picture', 'role',
            'is_email_verified', 'is_phone_verified', 'is_profile_complete',
            'address', 'city', 'state', 'country', 'postal_code',
            'shop_name', 'shop_owner_name', 'shop_logo',  # Barbershop fields
            'created_at', 'last_login'
        )
        read_only_fields = (
            'id', 'email', 'role', 'is_email_verified', 'is_phone_verified',
            'created_at', 'last_login'
        )
    
    def get_full_name(self, obj):
        """Return full name of the user"""
        return obj.get_full_name()
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        if value and not re.match(r'^\+?1?\d{9,15}$', value):
            raise serializers.ValidationError(
                "Phone number must be in valid format (e.g., +1234567890)"
            )
        return value


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing password
    """
    old_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    
    def validate_old_password(self, value):
        """Validate old password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value
    
    def validate_new_password(self, value):
        """Validate new password using Django's password validators"""
        try:
            validate_password(value, self.context['request'].user)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    
    def validate(self, attrs):
        """Validate password confirmation"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': "New password confirmation doesn't match."
            })
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for password reset request
    """
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Validate email exists"""
        try:
            user = User.objects.get(email=value.lower())
            if not user.is_active:
                raise serializers.ValidationError(
                    "User account is deactivated."
                )
        except User.DoesNotExist:
            # Don't reveal if email exists or not for security
            pass
        return value.lower()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for password reset confirmation
    """
    token = serializers.UUIDField(required=True)
    new_password = serializers.CharField(
        required=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    
    def validate_token(self, value):
        """Validate reset token"""
        try:
            reset_token = PasswordResetToken.objects.get(token=value)
            if not reset_token.is_valid:
                raise serializers.ValidationError(
                    "Invalid or expired reset token."
                )
            self.reset_token = reset_token
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError(
                "Invalid or expired reset token."
            )
        return value
    
    def validate_new_password(self, value):
        """Validate new password using Django's password validators"""
        try:
            # Get user from the token for password validation
            if hasattr(self, 'reset_token'):
                validate_password(value, self.reset_token.user)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    
    def validate(self, attrs):
        """Validate password confirmation"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': "New password confirmation doesn't match."
            })
        return attrs


class EmailVerificationSerializer(serializers.Serializer):
    """
    Serializer for email verification
    """
    token = serializers.UUIDField(required=True)
    
    def validate_token(self, value):
        """Validate verification token"""
        try:
            verification_token = EmailVerificationToken.objects.get(token=value)
            if not verification_token.is_valid:
                raise serializers.ValidationError(
                    "Invalid or expired verification token."
                )
            self.verification_token = verification_token
        except EmailVerificationToken.DoesNotExist:
            raise serializers.ValidationError(
                "Invalid or expired verification token."
            )
        return value


class ResendVerificationSerializer(serializers.Serializer):
    """
    Serializer for resending email verification
    """
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Validate email exists and is not already verified"""
        try:
            user = User.objects.get(email=value.lower())
            if user.is_email_verified:
                raise serializers.ValidationError(
                    "Email is already verified."
                )
            if not user.is_active:
                raise serializers.ValidationError(
                    "User account is deactivated."
                )
            self.user = user
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "No user found with this email address."
            )
        return value.lower()


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing users (admin only)
    """
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'full_name',
            'role', 'is_active', 'is_email_verified', 'created_at', 'last_login'
        )
    
    def get_full_name(self, obj):
        """Return full name of the user"""
        return obj.get_full_name()