"""
Serializers for Admin functionality
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import Activity, Appointment, AdminReport
from super_admin.models import Subscription


User = get_user_model()


class AdminStatsSerializer(serializers.Serializer):
    """
    Serializer for Admin dashboard statistics (scoped to admin's barbershops)
    """
    total_barbershops = serializers.IntegerField(read_only=True)
    active_barbershops = serializers.IntegerField(read_only=True)
    total_appointments = serializers.IntegerField(read_only=True)
    monthly_revenue = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)


class ActivitySerializer(serializers.ModelSerializer):
    """
    Serializer for Activity model
    """
    barbershop_name = serializers.CharField(source='barbershop.shop_name', read_only=True)
    barbershop_owner = serializers.CharField(source='barbershop.shop_owner_name', read_only=True)
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = Activity
        fields = [
            'id', 'barbershop', 'barbershop_name', 'barbershop_owner',
            'action_type', 'description', 'amount', 'timestamp', 'time_ago', 'metadata'
        ]
        read_only_fields = ['id', 'timestamp']
    
    def get_time_ago(self, obj):
        """Get human-readable time ago"""
        now = timezone.now()
        diff = now - obj.timestamp
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"


class AppointmentSerializer(serializers.ModelSerializer):
    """
    Serializer for Appointment model
    """
    barbershop_name = serializers.CharField(source='barbershop.shop_name', read_only=True)
    is_completed = serializers.BooleanField(read_only=True)
    is_revenue_generating = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'barbershop', 'barbershop_name', 'customer_name', 'customer_email',
            'customer_phone', 'service', 'amount', 'appointment_date', 'duration',
            'status', 'notes', 'is_completed', 'is_revenue_generating',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating appointments
    """
    class Meta:
        model = Appointment
        fields = [
            'barbershop', 'customer_name', 'customer_email', 'customer_phone',
            'service', 'amount', 'appointment_date', 'duration', 'notes'
        ]
    
    def validate_barbershop(self, value):
        """Validate that admin can create appointment for this barbershop"""
        request = self.context.get('request')
        if request and request.user.role == 'admin':
            if value.created_by != request.user:
                raise serializers.ValidationError("You can only create appointments for barbershops you manage.")
        return value
    
    def validate_appointment_date(self, value):
        """Validate appointment date is in the future"""
        if value <= timezone.now():
            raise serializers.ValidationError("Appointment date must be in the future.")
        return value


class AdminBarbershopListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing barbershops managed by admin (scoped)
    """
    subscription = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    total_appointments = serializers.SerializerMethodField()
    monthly_revenue = serializers.SerializerMethodField()
    last_activity = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'name', 'shop_name', 'shop_owner_name', 'shop_logo',
            'address', 'phone_number', 'role', 'is_active', 'is_email_verified',
            'created_at', 'updated_at', 'subscription', 'created_by_name', 
            'total_appointments', 'monthly_revenue', 'last_activity'
        ]
        read_only_fields = ['id', 'role', 'created_at', 'updated_at']
    
    def get_name(self, obj):
        """Get display name for barbershop"""
        return obj.shop_owner_name or obj.get_full_name()
    
    def get_created_by_name(self, obj):
        """Get name of admin who created this barbershop"""
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.email
        return 'Unknown'
    
    def get_subscription(self, obj):
        """Get subscription info"""
        try:
            subscription = obj.subscription
            return {
                'plan': subscription.plan,
                'status': subscription.status,
                'expires_at': subscription.expires_at,
                'is_active': subscription.is_active,
                'days_remaining': subscription.days_remaining
            }
        except:
            return None
    
    def get_total_appointments(self, obj):
        """Get total appointments for this barbershop"""
        return obj.appointments.count()
    
    def get_monthly_revenue(self, obj):
        """Get this month's revenue for this barbershop"""
        current_month = timezone.now().replace(day=1)
        revenue = obj.appointments.filter(
            appointment_date__gte=current_month,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        return revenue
    
    def get_last_activity(self, obj):
        """Get last activity for this barbershop"""
        try:
            last_activity = obj.activities.first()
            if last_activity:
                return {
                    'action_type': last_activity.action_type,
                    'description': last_activity.description,
                    'timestamp': last_activity.timestamp
                }
        except:
            pass
        return None


class AdminBarbershopCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating barbershop users (admin scoped)
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
        """Create barbershop user with subscription (created by current admin)"""
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
            created_by=self.context['request'].user,  # Set current admin as creator
            is_email_verified=True  # Auto-verify email for admin-created barbershops
        )
        user.set_password(password)
        user.save()
        
        # Create subscription
        Subscription.objects.create(
            user=user,
            plan=subscription_plan,
            status='active'
        )
        
        # Create activity
        Activity.objects.create(
            barbershop=user,
            action_type='profile_updated',
            description=f"Barbershop account created by {self.context['request'].user.get_full_name()}",
            metadata={
                'created_by': self.context['request'].user.id,
                'initial_plan': subscription_plan
            }
        )
        
        return user


class AdminBarbershopUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating barbershop users (admin scoped)
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
        
        # Track changes for activity log
        changes = []
        for field, value in validated_data.items():
            old_value = getattr(instance, field)
            if old_value != value:
                changes.append(f"{field}: {old_value} → {value}")
        
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
                changes.append(f"subscription plan: {subscription.plan} → {subscription_plan}")
                subscription.plan = subscription_plan
            
            if subscription_status and subscription.status != subscription_status:
                changes.append(f"subscription status: {subscription.status} → {subscription_status}")
                subscription.status = subscription_status
            
            subscription.save()
        
        # Create activity if there were changes
        if changes:
            Activity.objects.create(
                barbershop=instance,
                action_type='profile_updated',
                description=f"Profile updated by {self.context['request'].user.get_full_name()}: {', '.join(changes)}",
                metadata={
                    'updated_by': self.context['request'].user.id,
                    'changes': changes
                }
            )
        
        return instance


class AdminDashboardDataSerializer(serializers.Serializer):
    """
    Serializer for complete admin dashboard data
    """
    stats = AdminStatsSerializer(read_only=True)
    recent_activities = ActivitySerializer(many=True, read_only=True)
    recent_appointments = AppointmentSerializer(many=True, read_only=True)
    barbershop_summary = AdminBarbershopListSerializer(many=True, read_only=True)