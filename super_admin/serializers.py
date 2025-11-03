"""
Serializers for Super Admin functionality
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import Subscription, SubscriptionHistory


User = get_user_model()


class SuperAdminStatsSerializer(serializers.Serializer):
    """
    Serializer for Super Admin dashboard statistics
    """
    total_admins = serializers.IntegerField(read_only=True)
    total_barbershops = serializers.IntegerField(read_only=True)
    active_barbershops = serializers.IntegerField(read_only=True)
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    monthly_growth = serializers.FloatField(read_only=True)


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for Subscription model
    """
    is_expired = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'plan', 'status', 'started_at', 'expires_at',
            'features', 'max_appointments', 'max_staff',
            'is_expired', 'is_active', 'days_remaining',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'started_at', 'created_at', 'updated_at']


class AdminListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing admin users
    """
    managed_barbershops_count = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'role',
            'is_active', 'is_email_verified', 'created_at', 'updated_at',
            'managed_barbershops_count', 'created_by_name'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_managed_barbershops_count(self, obj):
        """Get count of barbershops managed by this admin"""
        return User.objects.filter(created_by=obj, role='barbershop').count()


class AdminCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating admin users
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'password', 'password_confirm'
        ]
    
    def validate(self, attrs):
        """Validate password confirmation"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs
    
    def validate_email(self, value):
        """Validate email uniqueness"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def create(self, validated_data):
        """Create admin user"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            **validated_data,
            role='admin',
            username=validated_data['email'],  # Use email as username
            created_by=self.context['request'].user,
            is_email_verified=True,  # Auto-verify admin users created by Super Admin
            is_active=True  # Make sure the user is active
        )
        user.set_password(password)
        user.save()
        
        return user


class AdminUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating admin users
    """
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'is_active', 'phone_number'
        ]
    
    def update(self, instance, validated_data):
        """Update admin user"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class BarbershopListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing barbershop users
    """
    subscription = SubscriptionSerializer(read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'name', 'shop_name', 'shop_owner_name', 'shop_logo',
            'address', 'phone_number', 'role', 'is_active', 'is_email_verified',
            'created_at', 'updated_at', 'subscription', 'created_by_name'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_name(self, obj):
        """Get display name for barbershop"""
        return obj.shop_owner_name or obj.get_full_name()


class BarbershopCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating barbershop users
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    subscription_plan = serializers.ChoiceField(
        choices=['basic', 'premium', 'enterprise'],
        default='basic',
        write_only=True
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'shop_name', 'shop_owner_name', 'shop_logo', 'address', 
            'phone_number', 'password', 'password_confirm', 'subscription_plan'
        ]
    
    def validate(self, attrs):
        """Validate password confirmation"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs
    
    def validate_email(self, value):
        """Validate email uniqueness"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_shop_name(self, value):
        """Validate shop name is provided"""
        if not value or not value.strip():
            raise serializers.ValidationError("Shop name is required.")
        return value
    
    def validate_shop_owner_name(self, value):
        """Validate shop owner name is provided"""
        if not value or not value.strip():
            raise serializers.ValidationError("Shop owner name is required.")
        return value
    
    @transaction.atomic
    def create(self, validated_data):
        """Create barbershop user with subscription"""
        subscription_plan = validated_data.pop('subscription_plan', 'basic')
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        # Create user
        user = User.objects.create_user(
            **validated_data,
            role='barbershop',
            username=validated_data['email'],  # Use email as username
            first_name=validated_data.get('shop_owner_name', ''),
            last_name='',
            created_by=self.context['request'].user,
            is_email_verified=True,  # Auto-verify barbershop users created by Super Admin
            is_active=True  # Make sure the user is active
        )
        user.set_password(password)
        user.save()
        
        # Create subscription
        Subscription.objects.create(
            user=user,
            plan=subscription_plan,
            status='active'
        )
        
        return user


class BarbershopUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating barbershop users
    """
    subscription_plan = serializers.ChoiceField(
        choices=['basic', 'premium', 'enterprise'],
        required=False,
        write_only=True
    )
    subscription_status = serializers.ChoiceField(
        choices=['active', 'inactive', 'suspended'],
        required=False,
        write_only=True
    )
    
    class Meta:
        model = User
        fields = [
            'shop_name', 'shop_owner_name', 'shop_logo', 'address', 
            'phone_number', 'is_active', 'subscription_plan', 'subscription_status'
        ]
    
    @transaction.atomic
    def update(self, instance, validated_data):
        """Update barbershop user and subscription"""
        subscription_plan = validated_data.pop('subscription_plan', None)
        subscription_status = validated_data.pop('subscription_status', None)
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update subscription if provided
        if subscription_plan or subscription_status:
            subscription, created = Subscription.objects.get_or_create(
                user=instance,
                defaults={'plan': subscription_plan or 'basic'}
            )
            
            if subscription_plan and subscription.plan != subscription_plan:
                # Log subscription change
                SubscriptionHistory.objects.create(
                    subscription=subscription,
                    action='plan_changed',
                    old_plan=subscription.plan,
                    new_plan=subscription_plan,
                    performed_by=self.context['request'].user
                )
                subscription.plan = subscription_plan
            
            if subscription_status and subscription.status != subscription_status:
                # Log status change
                SubscriptionHistory.objects.create(
                    subscription=subscription,
                    action='status_changed',
                    old_status=subscription.status,
                    new_status=subscription_status,
                    performed_by=self.context['request'].user
                )
                subscription.status = subscription_status
            
            subscription.save()
        
        return instance


class BarbershopDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for barbershop users
    """
    subscription = SubscriptionSerializer(read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'name', 'shop_name', 'shop_owner_name', 'shop_logo',
            'address', 'phone_number', 'role', 'is_active', 'is_email_verified',
            'date_of_birth', 'city', 'state', 'country', 'postal_code',
            'created_at', 'updated_at', 'subscription', 'created_by_name',
            'last_login', 'is_profile_complete'
        ]
        read_only_fields = ['id', 'role', 'created_at', 'updated_at', 'last_login']
    
    def get_name(self, obj):
        """Get display name for barbershop"""
        return obj.shop_owner_name or obj.get_full_name()


class UserStatusToggleSerializer(serializers.Serializer):
    """
    Serializer for toggling user active status
    """
    is_active = serializers.BooleanField()
    
    def update(self, instance, validated_data):
        """Toggle user active status"""
        instance.is_active = validated_data['is_active']
        instance.save()
        return instance


class ArchivedAdminSerializer(serializers.ModelSerializer):
    """
    Serializer for archived (soft-deleted) admin users
    """
    managed_barbershops_count = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    deleted_by_name = serializers.CharField(source='deleted_by.get_full_name', read_only=True)
    name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'name', 'role',
            'is_active', 'is_email_verified', 'created_at', 'updated_at',
            'deleted_at', 'deleted_by_name', 'managed_barbershops_count',
            'created_by_name'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    
    def get_name(self, obj):
        """Get display name for admin"""
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email
    
    def get_managed_barbershops_count(self, obj):
        """Get count of barbershops managed by this admin"""
        return User.objects.filter(created_by=obj, role='barbershop').count()


class ArchivedBarbershopSerializer(serializers.ModelSerializer):
    """
    Serializer for archived (soft-deleted) barbershop users
    """
    subscription = SubscriptionSerializer(read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    deleted_by_name = serializers.CharField(source='deleted_by.get_full_name', read_only=True)
    name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'name', 'shop_name', 'shop_owner_name', 'shop_logo',
            'address', 'phone_number', 'role', 'is_active', 'is_email_verified',
            'created_at', 'updated_at', 'deleted_at', 'deleted_by_name',
            'subscription', 'created_by_name'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    
    def get_name(self, obj):
        """Get display name for barbershop"""
        return obj.shop_owner_name or obj.get_full_name()