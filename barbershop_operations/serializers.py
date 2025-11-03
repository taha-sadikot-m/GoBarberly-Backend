"""
Serializers for Barbershop Operations
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
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

User = get_user_model()


class BarbershopProfileSerializer(serializers.ModelSerializer):
    """Serializer for barbershop profile"""
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'shop_name', 'shop_owner_name', 'shop_logo',
            'address', 'phone_number', 'first_name', 'last_name'
        ]
        read_only_fields = ['id', 'email']

    def validate(self, attrs):
        """Ensure the user is a barbershop user"""
        user = self.instance or self.context['request'].user
        if user.role != 'barbershop':
            raise serializers.ValidationError("Only barbershop users can access this profile.")
        return attrs

    def update(self, instance, validated_data):
        """Update barbershop profile with activity logging"""
        # Track changes for activity log
        changes = []
        for field, new_value in validated_data.items():
            old_value = getattr(instance, field)
            if old_value != new_value:
                if field == 'shop_logo':
                    changes.append(f"Logo updated")
                else:
                    field_name = field.replace('_', ' ').title()
                    changes.append(f"{field_name} changed")
        
        # Update the instance
        updated_instance = super().update(instance, validated_data)
        
        # Log activity if there were changes
        if changes:
            from .models import BarbershopActivityLog
            BarbershopActivityLog.objects.create(
                barbershop=updated_instance,
                action_type='profile_updated',
                description=f"Profile updated: {', '.join(changes)}",
                metadata={'changes': changes}
            )
        
        return updated_instance


class BarbershopAppointmentSerializer(serializers.ModelSerializer):
    """Serializer for barbershop appointments"""
    
    class Meta:
        model = BarbershopAppointment
        fields = [
            'id', 'customer_name', 'customer_phone', 'customer_email',
            'service', 'barber_name', 'appointment_date', 'appointment_time',
            'duration_minutes', 'status', 'notes', 'amount',
            'created_at', 'updated_at', 'is_today', 'is_completed'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_today', 'is_completed']

    def create(self, validated_data):
        # Automatically set barbershop to current user
        validated_data['barbershop'] = self.context['request'].user
        return super().create(validated_data)


class BarbershopAppointmentListSerializer(serializers.ModelSerializer):
    """Simplified serializer for appointment lists"""
    
    class Meta:
        model = BarbershopAppointment
        fields = [
            'id', 'customer_name', 'service', 'barber_name',
            'appointment_date', 'appointment_time', 'status',
            'amount', 'is_today'
        ]


class BarbershopSaleSerializer(serializers.ModelSerializer):
    """Serializer for barbershop sales"""
    
    class Meta:
        model = BarbershopSale
        fields = [
            'id', 'customer_name', 'service', 'barber_name', 'amount',
            'payment_method', 'appointment', 'notes', 'sale_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Automatically set barbershop to current user
        validated_data['barbershop'] = self.context['request'].user
        return super().create(validated_data)


class BarbershopSaleListSerializer(serializers.ModelSerializer):
    """Simplified serializer for sales lists"""
    
    class Meta:
        model = BarbershopSale
        fields = [
            'id', 'customer_name', 'service', 'barber_name',
            'amount', 'payment_method', 'sale_date'
        ]


class BarbershopStaffSerializer(serializers.ModelSerializer):
    """Serializer for barbershop staff"""
    
    class Meta:
        model = BarbershopStaff
        fields = [
            'id', 'name', 'role', 'phone', 'email', 'schedule',
            'status', 'salary', 'join_date', 'created_at', 'updated_at',
            'is_barber'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_barber']

    def create(self, validated_data):
        # Automatically set barbershop to current user
        validated_data['barbershop'] = self.context['request'].user
        return super().create(validated_data)


class BarbershopStaffListSerializer(serializers.ModelSerializer):
    """Serializer for staff lists with all required fields"""
    
    class Meta:
        model = BarbershopStaff
        fields = [
            'id', 'name', 'role', 'phone', 'email', 'schedule',
            'status', 'salary', 'join_date', 'created_at', 'updated_at',
            'is_barber'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_barber']


class BarbershopCustomerSerializer(serializers.ModelSerializer):
    """Serializer for barbershop customers"""
    
    class Meta:
        model = BarbershopCustomer
        fields = [
            'id', 'name', 'phone', 'email', 'notes',
            'total_visits', 'last_visit_date', 'total_spent',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'total_visits', 'last_visit_date', 'total_spent',
            'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        # Automatically set barbershop to current user
        validated_data['barbershop'] = self.context['request'].user
        return super().create(validated_data)


class BarbershopCustomerListSerializer(serializers.ModelSerializer):
    """Simplified serializer for customer lists"""
    
    class Meta:
        model = BarbershopCustomer
        fields = [
            'id', 'name', 'phone', 'email', 'total_visits',
            'last_visit_date', 'total_spent'
        ]


class BarbershopInventorySerializer(serializers.ModelSerializer):
    """Serializer for barbershop inventory"""
    
    class Meta:
        model = BarbershopInventory
        fields = [
            'id', 'name', 'category', 'quantity', 'min_stock',
            'unit_cost', 'selling_price', 'supplier', 'created_at', 'updated_at',
            'is_low_stock', 'stock_status', 'profit_margin', 'profit_per_unit'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'is_low_stock', 'stock_status', 
            'profit_margin', 'profit_per_unit'
        ]

    def create(self, validated_data):
        # Automatically set barbershop to current user
        validated_data['barbershop'] = self.context['request'].user
        return super().create(validated_data)


class BarbershopInventoryListSerializer(serializers.ModelSerializer):
    """Serializer for inventory lists with all required fields"""
    
    class Meta:
        model = BarbershopInventory
        fields = [
            'id', 'name', 'category', 'quantity', 'min_stock',
            'unit_cost', 'selling_price', 'supplier', 'created_at', 'updated_at',
            'stock_status', 'is_low_stock', 'profit_margin', 'profit_per_unit'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_low_stock', 'stock_status', 'profit_margin', 'profit_per_unit']


class BarbershopActivityLogSerializer(serializers.ModelSerializer):
    """Serializer for barbershop activity logs"""
    
    class Meta:
        model = BarbershopActivityLog
        fields = [
            'id', 'action_type', 'description', 'metadata',
            'created_at', 'appointment', 'sale', 'customer',
            'staff', 'inventory'
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        # Automatically set barbershop to current user
        validated_data['barbershop'] = self.context['request'].user
        return super().create(validated_data)


class BarbershopStaffAvailabilitySerializer(serializers.ModelSerializer):
    """Serializer for staff availability"""
    
    class Meta:
        model = BarbershopStaffAvailability
        fields = [
            'id', 'staff', 'date', 'start_time', 'end_time',
            'is_available', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# Dashboard Summary Serializers
class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    today_appointments = serializers.IntegerField()
    pending_appointments = serializers.IntegerField()
    completed_appointments = serializers.IntegerField()
    cancelled_appointments = serializers.IntegerField()
    today_sales = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_sales = serializers.DecimalField(max_digits=10, decimal_places=2)
    active_staff = serializers.IntegerField()
    total_customers = serializers.IntegerField()
    low_stock_items = serializers.IntegerField()


class MonthlyRevenueSerializer(serializers.Serializer):
    """Serializer for monthly revenue data"""
    month = serializers.CharField()
    revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    appointments = serializers.IntegerField()


class ServicePopularitySerializer(serializers.Serializer):
    """Serializer for service popularity data"""
    service = serializers.CharField()
    count = serializers.IntegerField()
    revenue = serializers.DecimalField(max_digits=12, decimal_places=2)


class StaffPerformanceSerializer(serializers.Serializer):
    """Serializer for staff performance data"""
    staff_name = serializers.CharField()
    total_services = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    avg_rating = serializers.DecimalField(max_digits=3, decimal_places=2, required=False)


# Additional serializers for comprehensive functionality
class BarbershopDashboardStatsSerializer(serializers.Serializer):
    """Enhanced dashboard statistics serializer"""
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    monthly_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_appointments = serializers.IntegerField()
    completed_appointments = serializers.IntegerField()
    pending_appointments = serializers.IntegerField()
    today_appointments = serializers.IntegerField()
    total_customers = serializers.IntegerField()
    total_staff = serializers.IntegerField()
    low_stock_items = serializers.IntegerField()
    customer_satisfaction = serializers.DecimalField(max_digits=3, decimal_places=1)


class BarbershopAppointmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating appointments"""
    
    class Meta:
        model = BarbershopAppointment
        fields = [
            'customer_name', 'customer_phone', 'customer_email',
            'service', 'barber_name', 'appointment_date', 'appointment_time',
            'duration_minutes', 'notes', 'amount'
        ]

    def create(self, validated_data):
        validated_data['barbershop'] = self.context['request'].user
        return super().create(validated_data)


class BarbershopSaleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating sales"""
    
    class Meta:
        model = BarbershopSale
        fields = [
            'customer_name', 'service', 'barber_name', 'amount',
            'payment_method', 'notes', 'sale_date'
        ]

    def create(self, validated_data):
        validated_data['barbershop'] = self.context['request'].user
        return super().create(validated_data)


class BarbershopStaffCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating staff"""
    
    class Meta:
        model = BarbershopStaff
        fields = [
            'name', 'role', 'phone', 'email', 'schedule',
            'status', 'salary', 'join_date'
        ]

    def create(self, validated_data):
        validated_data['barbershop'] = self.context['request'].user
        return super().create(validated_data)


class BarbershopCustomerCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating customers"""
    
    class Meta:
        model = BarbershopCustomer
        fields = ['name', 'phone', 'email', 'notes']

    def create(self, validated_data):
        validated_data['barbershop'] = self.context['request'].user
        return super().create(validated_data)


class BarbershopInventoryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating inventory items"""
    
    class Meta:
        model = BarbershopInventory
        fields = [
            'name', 'category', 'quantity', 'min_stock',
            'unit_cost', 'selling_price', 'supplier'
        ]

    def create(self, validated_data):
        validated_data['barbershop'] = self.context['request'].user
        return super().create(validated_data)


class BarbershopReportsDataSerializer(serializers.Serializer):
    """Serializer for reports data"""
    date_range = serializers.DictField()
    revenue = serializers.DictField()
    appointments = serializers.DictField()
    services = serializers.ListField()
    staff_performance = serializers.ListField()


class CalendarDataSerializer(serializers.Serializer):
    """Serializer for calendar data"""
    month = serializers.IntegerField()
    year = serializers.IntegerField()
    appointments = serializers.DictField()


class ScheduleGridSerializer(serializers.Serializer):
    """Serializer for schedule grid data"""
    date = serializers.CharField()
    staff = serializers.ListField()
    time_slots = serializers.ListField()
    appointments = serializers.ListField()


# Service Serializers
class BarbershopServiceSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating barbershop services"""
    formatted_price = serializers.ReadOnlyField()
    
    class Meta:
        model = BarbershopService
        fields = [
            'id', 'name', 'price', 'description',
            'is_active', 'formatted_price', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'formatted_price']

    def create(self, validated_data):
        validated_data['barbershop'] = self.context['request'].user
        return super().create(validated_data)


class BarbershopServiceListSerializer(serializers.ModelSerializer):
    """Simplified serializer for service lists"""
    formatted_price = serializers.ReadOnlyField()
    
    class Meta:
        model = BarbershopService
        fields = [
            'id', 'name', 'price', 'description', 'formatted_price',
            'is_active', 'created_at', 'updated_at'
        ]


class SalesAnalyticsSerializer(serializers.Serializer):
    """Serializer for sales analytics"""
    date_range = serializers.DictField()
    daily_revenue = serializers.ListField()
    service_performance = serializers.ListField()
    customer_retention = serializers.DictField()
    peak_hours = serializers.ListField()