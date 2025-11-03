from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
import uuid
from datetime import timedelta


class UserManager(BaseUserManager):
    """Custom manager for User model with soft delete support"""
    
    def get_queryset(self):
        """Return the default queryset"""
        return super().get_queryset()
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user"""
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        extra_fields.setdefault('username', email)  # Use email as username
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'super_admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)
    
    def get_by_natural_key(self, username):
        """Get user by natural key (email in our case)"""
        return self.get(**{self.model.USERNAME_FIELD: username})
    
    def active(self):
        """Return only active (non-deleted) users"""
        return self.get_queryset().filter(deleted_at__isnull=True)
    
    def deleted(self):
        """Return only soft-deleted users"""
        return self.get_queryset().filter(deleted_at__isnull=False)
    
    def with_role(self, role):
        """Return users with specific role"""
        return self.get_queryset().filter(role=role)
    
    def active_with_role(self, role):
        """Return active users with specific role"""
        return self.active().filter(role=role)
    
    def deleted_with_role(self, role):
        """Return deleted users with specific role"""
        return self.deleted().filter(role=role)


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    """
    USER_ROLES = (
        ('customer', 'Customer'),
        ('barber', 'Barber'),
        ('barbershop', 'Barbershop'),  # Updated to match frontend
        ('admin', 'Admin'),
        ('super_admin', 'Super Admin'),  # Updated to match frontend
    )
    
    # Override email to be unique and required
    email = models.EmailField(unique=True, db_index=True)
    
    # Additional user fields
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    # Role and permissions
    role = models.CharField(max_length=20, choices=USER_ROLES, default='customer')
    
    # Barbershop specific fields
    shop_name = models.CharField(max_length=255, blank=True, null=True)
    shop_owner_name = models.CharField(max_length=255, blank=True, null=True)
    shop_logo = models.ImageField(upload_to='shop_logos/', blank=True, null=True)
    
    # Account status fields
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    is_profile_complete = models.BooleanField(default=False)
    
    # Audit fields
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_users')
    
    # Soft delete fields
    deleted_at = models.DateTimeField(null=True, blank=True, help_text="Timestamp when user was soft deleted")
    deleted_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='deleted_users', help_text="User who performed the soft delete")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    
    # Address information
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    
    # Use email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    # Custom manager
    objects = UserManager()
    
    class Meta:
        db_table = 'accounts_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.email} ({self.get_full_name()})"
    
    def get_full_name(self):
        """Return the full name of the user"""
        return f"{self.first_name} {self.last_name}".strip() or self.email
    
    def get_display_name(self):
        """Return display name (full name or username)"""
        full_name = self.get_full_name()
        return full_name if full_name != self.email else self.username
    
    def natural_key(self):
        """Return the natural key for this user"""
        return (self.email,)
    
    @property
    def is_admin_user(self):
        """Check if user has admin privileges"""
        return self.role in ['admin', 'super_admin'] or self.is_superuser
    
    @property
    def can_manage_shop(self):
        """Check if user can manage barbershop"""
        return self.role in ['shop_owner', 'admin', 'super_admin'] or self.is_superuser
    
    @property
    def is_deleted(self):
        """Check if user is soft deleted"""
        return self.deleted_at is not None
    
    def soft_delete(self, deleted_by=None):
        """Soft delete the user"""
        if not self.is_deleted:
            self.deleted_at = timezone.now()
            self.deleted_by = deleted_by
            self.is_active = False  # Also deactivate the user
            self.save(update_fields=['deleted_at', 'deleted_by', 'is_active'])
    
    def restore(self):
        """Restore a soft deleted user"""
        if self.is_deleted:
            self.deleted_at = None
            self.deleted_by = None
            self.is_active = True  # Reactivate the user
            self.save(update_fields=['deleted_at', 'deleted_by', 'is_active'])


class EmailVerificationToken(models.Model):
    """
    Model to store email verification tokens
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_verification_tokens')
    token = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'accounts_email_verification_token'
        verbose_name = 'Email Verification Token'
        verbose_name_plural = 'Email Verification Tokens'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Token expires in 24 hours
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Email verification token for {self.user.email}"
    
    @property
    def is_expired(self):
        """Check if token is expired"""
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        """Check if token is valid (not used and not expired)"""
        return not self.is_used and not self.is_expired


class PasswordResetToken(models.Model):
    """
    Model to store password reset tokens
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'accounts_password_reset_token'
        verbose_name = 'Password Reset Token'
        verbose_name_plural = 'Password Reset Tokens'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Token expires in 1 hour
            self.expires_at = timezone.now() + timedelta(hours=1)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Password reset token for {self.user.email}"
    
    @property
    def is_expired(self):
        """Check if token is expired"""
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        """Check if token is valid (not used and not expired)"""
        return not self.is_used and not self.is_expired


class UserSession(models.Model):
    """
    Model to track user sessions for security purposes
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True, db_index=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    device_info = models.JSONField(blank=True, null=True)
    login_time = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'accounts_user_session'
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        ordering = ['-login_time']
    
    def __str__(self):
        return f"Session for {self.user.email} from {self.ip_address}"
    
    @property
    def is_current_session(self):
        """Check if this is the current active session"""
        return self.is_active and (timezone.now() - self.last_activity).seconds < 3600  # 1 hour


class UserLoginHistory(models.Model):
    """
    Model to track user login history for security and analytics
    """
    LOGIN_STATUS_CHOICES = (
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('blocked', 'Blocked'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history', blank=True, null=True)
    email = models.EmailField(db_index=True)  # Store email even for failed attempts
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=LOGIN_STATUS_CHOICES)
    failure_reason = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'accounts_user_login_history'
        verbose_name = 'User Login History'
        verbose_name_plural = 'User Login History'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['email', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.email} - {self.status} at {self.timestamp}"
