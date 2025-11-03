from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import (
    User, 
    EmailVerificationToken, 
    PasswordResetToken, 
    UserSession, 
    UserLoginHistory
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin interface for User model
    """
    list_display = (
        'email', 'username', 'first_name', 'last_name', 'role', 
        'is_email_verified', 'is_active', 'created_at'
    )
    list_filter = (
        'role', 'is_email_verified', 'is_active', 'is_staff', 
        'is_superuser', 'created_at'
    )
    search_fields = ('email', 'username', 'first_name', 'last_name', 'phone_number')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'last_login_ip')
    
    fieldsets = (
        ('Authentication', {
            'fields': ('email', 'username', 'password')
        }),
        ('Personal Info', {
            'fields': (
                'first_name', 'last_name', 'phone_number', 
                'date_of_birth', 'profile_picture'
            )
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'country', 'postal_code'),
            'classes': ('collapse',)
        }),
        ('Permissions & Role', {
            'fields': (
                'role', 'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            )
        }),
        ('Account Status', {
            'fields': (
                'is_email_verified', 'is_phone_verified', 
                'is_profile_complete'
            )
        }),
        ('Important Dates', {
            'fields': (
                'last_login', 'last_login_ip', 'date_joined', 
                'created_at', 'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('Required Information', {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'first_name', 'last_name', 
                'password1', 'password2', 'role'
            ),
        }),
    )


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    """
    Admin interface for Email Verification Tokens
    """
    list_display = (
        'user_email', 'token_short', 'created_at', 
        'expires_at', 'is_used', 'is_expired_status'
    )
    list_filter = ('is_used', 'created_at', 'expires_at')
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('token', 'created_at', 'expires_at')
    ordering = ('-created_at',)
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    
    def token_short(self, obj):
        return f"{str(obj.token)[:8]}..."
    token_short.short_description = 'Token'
    
    def is_expired_status(self, obj):
        if obj.is_expired:
            return format_html('<span style="color: red;">Expired</span>')
        return format_html('<span style="color: green;">Valid</span>')
    is_expired_status.short_description = 'Status'


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """
    Admin interface for Password Reset Tokens
    """
    list_display = (
        'user_email', 'token_short', 'created_at', 
        'expires_at', 'is_used', 'ip_address', 'is_expired_status'
    )
    list_filter = ('is_used', 'created_at', 'expires_at')
    search_fields = ('user__email', 'user__username', 'ip_address')
    readonly_fields = ('token', 'created_at', 'expires_at', 'ip_address', 'user_agent')
    ordering = ('-created_at',)
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    
    def token_short(self, obj):
        return f"{str(obj.token)[:8]}..."
    token_short.short_description = 'Token'
    
    def is_expired_status(self, obj):
        if obj.is_expired:
            return format_html('<span style="color: red;">Expired</span>')
        return format_html('<span style="color: green;">Valid</span>')
    is_expired_status.short_description = 'Status'


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """
    Admin interface for User Sessions
    """
    list_display = (
        'user_email', 'session_key_short', 'ip_address', 
        'login_time', 'last_activity', 'is_active', 'is_current_status'
    )
    list_filter = ('is_active', 'login_time', 'last_activity')
    search_fields = ('user__email', 'session_key', 'ip_address')
    readonly_fields = (
        'session_key', 'login_time', 'last_activity', 
        'ip_address', 'user_agent', 'device_info'
    )
    ordering = ('-login_time',)
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    
    def session_key_short(self, obj):
        return f"{obj.session_key[:8]}..."
    session_key_short.short_description = 'Session'
    
    def is_current_status(self, obj):
        if obj.is_current_session:
            return format_html('<span style="color: green;">Current</span>')
        return format_html('<span style="color: gray;">Inactive</span>')
    is_current_status.short_description = 'Current'


@admin.register(UserLoginHistory)
class UserLoginHistoryAdmin(admin.ModelAdmin):
    """
    Admin interface for User Login History
    """
    list_display = (
        'email', 'status_colored', 'ip_address', 
        'timestamp', 'failure_reason'
    )
    list_filter = ('status', 'timestamp')
    search_fields = ('email', 'ip_address', 'user__username')
    readonly_fields = (
        'user', 'email', 'ip_address', 'user_agent', 
        'status', 'failure_reason', 'timestamp'
    )
    ordering = ('-timestamp',)
    
    def status_colored(self, obj):
        colors = {
            'success': 'green',
            'failed': 'red',
            'blocked': 'orange'
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {};">{}</span>', 
            color, obj.get_status_display()
        )
    status_colored.short_description = 'Status'
    
    def has_add_permission(self, request):
        # Prevent manual addition of login history
        return False
    
    def has_change_permission(self, request, obj=None):
        # Prevent modification of login history
        return False


# Register admin site customizations
admin.site.site_header = "GoBarberly Administration"
admin.site.site_title = "GoBarberly Admin"
admin.site.index_title = "Welcome to GoBarberly Administration"
