from django.db import models
from django.utils import timezone
from decimal import Decimal


class Activity(models.Model):
    """
    Model to track activities for barbershops managed by admins
    """
    ACTION_TYPES = (
        ('service_update', 'Service Update'),
        ('appointment_added', 'Appointment Added'),
        ('payment_processed', 'Payment Processed'),
        ('profile_updated', 'Profile Updated'),
        ('status_changed', 'Status Changed'),
        ('subscription_changed', 'Subscription Changed'),
        ('staff_added', 'Staff Added'),
        ('hours_updated', 'Hours Updated'),
    )
    
    barbershop = models.ForeignKey(
        'accounts.User', 
        on_delete=models.CASCADE, 
        related_name='activities',
        limit_choices_to={'role': 'barbershop'},
        help_text="The barbershop this activity belongs to"
    )
    action_type = models.CharField(
        max_length=50, 
        choices=ACTION_TYPES,
        help_text="Type of activity performed"
    )
    description = models.TextField(
        help_text="Detailed description of the activity"
    )
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Amount associated with activity (for payments/revenue)"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When the activity occurred"
    )
    metadata = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Additional activity data"
    )
    
    class Meta:
        db_table = 'admin_activity'
        verbose_name = 'Activity'
        verbose_name_plural = 'Activities'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['barbershop', '-timestamp']),
            models.Index(fields=['action_type', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.barbershop.shop_name or self.barbershop.email} - {self.action_type} - {self.timestamp}"


class Appointment(models.Model):
    """
    Basic appointment model for tracking statistics
    """
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    )
    
    barbershop = models.ForeignKey(
        'accounts.User', 
        on_delete=models.CASCADE, 
        related_name='appointments',
        limit_choices_to={'role': 'barbershop'},
        help_text="The barbershop where appointment is scheduled"
    )
    customer_name = models.CharField(
        max_length=255,
        help_text="Name of the customer"
    )
    customer_email = models.EmailField(
        blank=True, 
        null=True,
        help_text="Customer email address"
    )
    customer_phone = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        help_text="Customer phone number"
    )
    service = models.CharField(
        max_length=255,
        help_text="Service(s) requested"
    )
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Total appointment cost"
    )
    appointment_date = models.DateTimeField(
        help_text="Scheduled appointment date and time"
    )
    duration = models.PositiveIntegerField(
        default=60,
        help_text="Appointment duration in minutes"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='scheduled',
        help_text="Current appointment status"
    )
    notes = models.TextField(
        blank=True, 
        null=True,
        help_text="Additional notes about the appointment"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the appointment was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the appointment was last updated"
    )
    
    class Meta:
        db_table = 'admin_appointment'
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
        ordering = ['-appointment_date']
        indexes = [
            models.Index(fields=['barbershop', '-appointment_date']),
            models.Index(fields=['status', '-appointment_date']),
            models.Index(fields=['appointment_date']),
        ]
    
    def __str__(self):
        return f"{self.customer_name} - {self.service} - {self.appointment_date.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def is_completed(self):
        """Check if appointment is completed"""
        return self.status == 'completed'
    
    @property
    def is_revenue_generating(self):
        """Check if appointment generates revenue"""
        return self.status in ['completed', 'in_progress']
    
    def save(self, *args, **kwargs):
        """Override save to create activity when appointment is created/updated"""
        is_new = self.pk is None
        old_status = None
        
        if not is_new:
            old_appointment = Appointment.objects.get(pk=self.pk)
            old_status = old_appointment.status
        
        super().save(*args, **kwargs)
        
        # Create activity for new appointments
        if is_new:
            Activity.objects.create(
                barbershop=self.barbershop,
                action_type='appointment_added',
                description=f"New appointment scheduled for {self.customer_name} - {self.service}",
                amount=self.amount if self.status in ['completed', 'confirmed'] else None,
                metadata={
                    'appointment_id': self.id,
                    'customer_name': self.customer_name,
                    'service': self.service,
                    'appointment_date': self.appointment_date.isoformat(),
                }
            )
        
        # Create activity for completed appointments (revenue)
        elif old_status != 'completed' and self.status == 'completed':
            Activity.objects.create(
                barbershop=self.barbershop,
                action_type='payment_processed',
                description=f"Payment processed for {self.customer_name} - {self.service}",
                amount=self.amount,
                metadata={
                    'appointment_id': self.id,
                    'customer_name': self.customer_name,
                    'service': self.service,
                }
            )


class AdminReport(models.Model):
    """
    Model for storing generated admin reports
    """
    REPORT_TYPES = (
        ('monthly_summary', 'Monthly Summary'),
        ('barbershop_performance', 'Barbershop Performance'),
        ('revenue_analysis', 'Revenue Analysis'),
        ('appointment_trends', 'Appointment Trends'),
    )
    
    admin_user = models.ForeignKey(
        'accounts.User', 
        on_delete=models.CASCADE, 
        related_name='reports',
        limit_choices_to={'role': 'admin'},
        help_text="Admin who generated this report"
    )
    report_type = models.CharField(
        max_length=50, 
        choices=REPORT_TYPES,
        help_text="Type of report generated"
    )
    title = models.CharField(
        max_length=255,
        help_text="Report title"
    )
    data = models.JSONField(
        help_text="Report data in JSON format"
    )
    period_start = models.DateField(
        help_text="Start date for report period"
    )
    period_end = models.DateField(
        help_text="End date for report period"
    )
    generated_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the report was generated"
    )
    
    class Meta:
        db_table = 'admin_report'
        verbose_name = 'Admin Report'
        verbose_name_plural = 'Admin Reports'
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['admin_user', '-generated_at']),
            models.Index(fields=['report_type', '-generated_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.admin_user.get_full_name()} - {self.generated_at.strftime('%Y-%m-%d')}"
