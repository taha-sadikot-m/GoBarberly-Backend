"""
Models for Barbershop Operations
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid

User = get_user_model()


def get_current_date():
    """Helper function to get current date (not datetime)"""
    return timezone.now().date()


class BarbershopAppointment(models.Model):
    """
    Appointment model for barbershop users
    """
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('no_show', 'No Show'),
    ]
    
    SERVICE_CHOICES = [
        ('Haircut', 'Haircut - ₹300'),
        ('Beard Trim', 'Beard Trim - ₹200'),
        ('Hair + Beard', 'Hair + Beard - ₹450'),
        ('Shave', 'Shave - ₹250'),
        ('Hair Color', 'Hair Color - ₹500'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    barbershop = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='barbershop_appointments',
        limit_choices_to={'role': 'barbershop'}
    )
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=20)
    customer_email = models.EmailField(blank=True, null=True)
    service = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    barber_name = models.CharField(max_length=100)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    notes = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-appointment_date', '-appointment_time']
        indexes = [
            models.Index(fields=['barbershop', 'appointment_date']),
            models.Index(fields=['barbershop', 'status']),
            models.Index(fields=['barber_name', 'appointment_date']),
        ]
    
    def __str__(self):
        return f"{self.customer_name} - {self.service} on {self.appointment_date}"
    
    @property
    def is_today(self):
        return self.appointment_date == timezone.now().date()
    
    @property
    def is_completed(self):
        return self.status == 'completed'


class BarbershopSale(models.Model):
    """
    Sales transaction model for barbershop users
    """
    PAYMENT_CHOICES = [
        ('Cash', 'Cash'),
        ('UPI', 'UPI'),
        ('Card', 'Card'),
        ('Paytm', 'Paytm'),
    ]
    
    SERVICE_CHOICES = [
        ('Haircut', 'Haircut'),
        ('Beard Trim', 'Beard Trim'),
        ('Hair + Beard', 'Hair + Beard'),
        ('Shave', 'Shave'),
        ('Hair Color', 'Hair Color'),
    ]
    
    id = models.AutoField(primary_key=True)
    barbershop = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='barbershop_sales',
        limit_choices_to={'role': 'barbershop'}
    )
    customer_name = models.CharField(max_length=100)
    service = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    barber_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    
    # Link to appointment if sale is from an appointment
    appointment = models.OneToOneField(
        BarbershopAppointment, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='sale'
    )
    
    notes = models.TextField(blank=True)
    sale_date = models.DateField(default=get_current_date)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-sale_date', '-created_at']
        indexes = [
            models.Index(fields=['barbershop', 'sale_date']),
            models.Index(fields=['barbershop', 'payment_method']),
            models.Index(fields=['barber_name', 'sale_date']),
        ]
    
    def __str__(self):
        return f"₹{self.amount} - {self.service} by {self.barber_name}"


class BarbershopStaff(models.Model):
    """
    Staff management model for barbershop users
    """
    ROLE_CHOICES = [
        ('Barber', 'Barber'),
        ('Senior Barber', 'Senior Barber'),
        ('Manager', 'Manager'),
        ('Receptionist', 'Receptionist'),
    ]
    
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('On Leave', 'On Leave'),
    ]
    
    barbershop = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='barbershop_staff',
        limit_choices_to={'role': 'barbershop'}
    )
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    schedule = models.TextField(help_text="Working hours and days")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    
    # Salary and employment details
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    join_date = models.DateField(default=get_current_date)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['barbershop', 'status']),
            models.Index(fields=['barbershop', 'role']),
        ]
        unique_together = ['barbershop', 'phone']  # Unique phone per barbershop
    
    def __str__(self):
        return f"{self.name} - {self.role}"
    
    @property
    def is_barber(self):
        return self.role in ['Barber', 'Senior Barber']


class BarbershopCustomer(models.Model):
    """
    Customer management model for barbershop users
    """
    barbershop = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='barbershop_customers',
        limit_choices_to={'role': 'barbershop'}
    )
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    notes = models.TextField(blank=True, help_text="Preferences, allergies, etc.")
    
    # Visit tracking
    total_visits = models.PositiveIntegerField(default=0)
    last_visit_date = models.DateField(null=True, blank=True)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-last_visit_date', 'name']
        indexes = [
            models.Index(fields=['barbershop', 'phone']),
            models.Index(fields=['barbershop', 'last_visit_date']),
        ]
        unique_together = ['barbershop', 'phone']  # Unique phone per barbershop
    
    def __str__(self):
        return f"{self.name} - {self.phone}"
    
    def update_visit_stats(self):
        """Update visit statistics from appointments and sales"""
        # Count completed appointments
        appointments = self.barbershop.barbershop_appointments.filter(
            customer_name=self.name,
            status='completed'
        )
        self.total_visits = appointments.count()
        
        if appointments.exists():
            self.last_visit_date = appointments.first().appointment_date
        
        # Calculate total spent from sales
        sales = self.barbershop.barbershop_sales.filter(customer_name=self.name)
        self.total_spent = sum(sale.amount for sale in sales)
        
        self.save()


class BarbershopInventory(models.Model):
    """
    Inventory management model for barbershop users
    """
    CATEGORY_CHOICES = [
        ('Hair Products', 'Hair Products'),
        ('Shaving', 'Shaving'),
        ('Tools', 'Tools'),
        ('Cleaning', 'Cleaning'),
        ('Other', 'Other'),
    ]
    
    barbershop = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='barbershop_inventory',
        limit_choices_to={'role': 'barbershop'}
    )
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    quantity = models.PositiveIntegerField(default=0)
    min_stock = models.PositiveIntegerField(default=5, help_text="Minimum stock level for alerts")
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Cost price per unit")
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Selling price per unit")
    supplier = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['barbershop', 'category']),
            models.Index(fields=['barbershop', 'quantity']),
        ]
        unique_together = ['barbershop', 'name']  # Unique item name per barbershop
        verbose_name_plural = "Barbershop Inventory"
    
    def __str__(self):
        return f"{self.name} ({self.quantity})"
    
    @property
    def is_low_stock(self):
        return self.quantity <= self.min_stock
    
    @property
    def stock_status(self):
        if self.quantity == 0:
            return 'out_of_stock'
        elif self.is_low_stock:
            return 'low_stock'
        else:
            return 'in_stock'
    
    @property
    def profit_margin(self):
        """Calculate profit margin percentage"""
        if self.unit_cost > 0 and self.selling_price > 0:
            return ((self.selling_price - self.unit_cost) / self.unit_cost) * 100
        return 0
    
    @property
    def profit_per_unit(self):
        """Calculate profit per unit"""
        if self.selling_price > 0 and self.unit_cost > 0:
            return self.selling_price - self.unit_cost
        return 0


class BarbershopActivityLog(models.Model):
    """
    Activity logging model for barbershop users
    """
    ACTION_CHOICES = [
        ('appointment_created', 'Appointment Created'),
        ('appointment_updated', 'Appointment Updated'),
        ('appointment_cancelled', 'Appointment Cancelled'),
        ('appointment_completed', 'Appointment Completed'),
        ('sale_recorded', 'Sale Recorded'),
        ('sale_updated', 'Sale Updated'),
        ('staff_added', 'Staff Added'),
        ('staff_updated', 'Staff Updated'),
        ('customer_added', 'Customer Added'),
        ('customer_updated', 'Customer Updated'),
        ('inventory_added', 'Inventory Added'),
        ('inventory_updated', 'Inventory Updated'),
        ('inventory_low_stock', 'Low Stock Alert'),
        ('service_added', 'Service Added'),
        ('service_updated', 'Service Updated'),
        ('service_deleted', 'Service Deleted'),
        ('login', 'User Login'),
        ('profile_updated', 'Profile Updated'),
        ('settings_changed', 'Settings Changed'),
    ]
    
    barbershop = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='barbershop_activity_logs',
        limit_choices_to={'role': 'barbershop'}
    )
    action_type = models.CharField(max_length=30, choices=ACTION_CHOICES)
    description = models.TextField()
    
    # Optional references to related objects
    appointment = models.ForeignKey(BarbershopAppointment, on_delete=models.SET_NULL, null=True, blank=True)
    sale = models.ForeignKey(BarbershopSale, on_delete=models.SET_NULL, null=True, blank=True)
    customer = models.ForeignKey(BarbershopCustomer, on_delete=models.SET_NULL, null=True, blank=True)
    staff = models.ForeignKey(BarbershopStaff, on_delete=models.SET_NULL, null=True, blank=True)
    inventory = models.ForeignKey(BarbershopInventory, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Additional metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['barbershop', 'action_type']),
            models.Index(fields=['barbershop', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.action_type} - {self.description[:50]}"


class BarbershopStaffAvailability(models.Model):
    """
    Staff availability and schedule overrides
    """
    staff = models.ForeignKey(
        BarbershopStaff, 
        on_delete=models.CASCADE, 
        related_name='availability_overrides'
    )
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)  # None means unavailable
    end_time = models.TimeField(null=True, blank=True)
    is_available = models.BooleanField(default=True)
    notes = models.CharField(max_length=200, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['date', 'start_time']
        unique_together = ['staff', 'date', 'start_time']
        indexes = [
            models.Index(fields=['staff', 'date']),
            models.Index(fields=['staff', 'date', 'start_time']),
        ]
    
    def __str__(self):
        availability = "Available" if self.is_available else "Unavailable"
        if self.start_time and self.end_time:
            return f"{self.staff.name} on {self.date}: {self.start_time}-{self.end_time}"
        return f"{self.staff.name} on {self.date}: {availability}"


class BarbershopService(models.Model):
    """
    Service model for barbershop services with pricing
    """
    barbershop = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='barbershop_services',
        limit_choices_to={'role': 'barbershop'}
    )
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        unique_together = ['barbershop', 'name']
        indexes = [
            models.Index(fields=['barbershop', 'is_active']),
            models.Index(fields=['barbershop', 'name']),
        ]
    
    def __str__(self):
        return f"{self.name} - ₹{self.price}"
    
    @property
    def formatted_price(self):
        return f"₹{self.price}"
