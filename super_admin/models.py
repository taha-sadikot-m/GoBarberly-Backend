from django.db import models
from django.utils import timezone
from datetime import timedelta


class Subscription(models.Model):
    """
    Subscription model for barbershop users
    """
    PLAN_CHOICES = (
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('expired', 'Expired'),
    )
    
    user = models.OneToOneField(
        'accounts.User', 
        on_delete=models.CASCADE, 
        related_name='subscription',
        help_text="The barbershop user this subscription belongs to"
    )
    plan = models.CharField(
        max_length=20, 
        choices=PLAN_CHOICES, 
        default='basic',
        help_text="Subscription plan type"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='active',
        help_text="Current subscription status"
    )
    started_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the subscription started"
    )
    expires_at = models.DateTimeField(
        help_text="When the subscription expires"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional subscription details
    features = models.JSONField(
        default=dict, 
        blank=True,
        help_text="JSON field for plan-specific features"
    )
    max_appointments = models.PositiveIntegerField(
        default=100,
        help_text="Maximum appointments per month"
    )
    max_staff = models.PositiveIntegerField(
        default=5,
        help_text="Maximum staff members allowed"
    )
    
    class Meta:
        db_table = 'super_admin_subscription'
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'expires_at']),
            models.Index(fields=['plan', 'status']),
        ]
    
    def save(self, *args, **kwargs):
        # Set default expiration date if not provided (1 year from now)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=365)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.shop_name or self.user.email} - {self.plan} ({self.status})"
    
    @property
    def is_expired(self):
        """Check if subscription is expired"""
        return timezone.now() > self.expires_at
    
    @property
    def is_active(self):
        """Check if subscription is active and not expired"""
        return self.status == 'active' and not self.is_expired
    
    @property
    def days_remaining(self):
        """Get number of days remaining in subscription"""
        if self.is_expired:
            return 0
        return (self.expires_at - timezone.now()).days
    
    def update_status(self):
        """Update subscription status based on expiration"""
        if self.is_expired and self.status == 'active':
            self.status = 'expired'
            self.save()


class SubscriptionHistory(models.Model):
    """
    Track subscription changes and upgrades/downgrades
    """
    subscription = models.ForeignKey(
        Subscription, 
        on_delete=models.CASCADE, 
        related_name='history'
    )
    action = models.CharField(max_length=50)  # 'created', 'upgraded', 'downgraded', 'renewed', 'suspended'
    old_plan = models.CharField(max_length=20, blank=True, null=True)
    new_plan = models.CharField(max_length=20, blank=True, null=True)
    old_status = models.CharField(max_length=20, blank=True, null=True)
    new_status = models.CharField(max_length=20, blank=True, null=True)
    performed_by = models.ForeignKey(
        'accounts.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Admin/Super Admin who performed this action"
    )
    notes = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'super_admin_subscription_history'
        verbose_name = 'Subscription History'
        verbose_name_plural = 'Subscription History'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.subscription.user.shop_name} - {self.action} at {self.timestamp}"
