from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from .models import EmailVerificationToken, PasswordResetToken
import logging

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """
    Get client IP address from request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """
    Get user agent from request
    """
    return request.META.get('HTTP_USER_AGENT', '')


def send_verification_email(user, request):
    """
    Send email verification email to user
    """
    try:
        # Create verification token
        verification_token = EmailVerificationToken.objects.create(user=user)
        
        # Build verification URL
        verification_url = request.build_absolute_uri(
            f"/api/auth/verify-email/?token={verification_token.token}"
        )
        
        # Email context
        context = {
            'user': user,
            'verification_url': verification_url,
            'site_name': 'GoBarberly',
            'support_email': settings.DEFAULT_FROM_EMAIL,
        }
        
        # Render email templates
        subject = f"Verify your email address - {context['site_name']}"
        html_message = render_to_string('emails/email_verification.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Verification email sent successfully to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
        raise e


def send_password_reset_email(user, request):
    """
    Send password reset email to user
    """
    try:
        # Create reset token
        reset_token = PasswordResetToken.objects.create(
            user=user,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        
        # Build reset URL
        reset_url = request.build_absolute_uri(
            f"/api/auth/reset-password/?token={reset_token.token}"
        )
        
        # Email context
        context = {
            'user': user,
            'reset_url': reset_url,
            'site_name': 'GoBarberly',
            'support_email': settings.DEFAULT_FROM_EMAIL,
            'valid_hours': 1,  # Token valid for 1 hour
        }
        
        # Render email templates
        subject = f"Password Reset Request - {context['site_name']}"
        html_message = render_to_string('emails/password_reset.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Password reset email sent successfully to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
        raise e


def send_welcome_email(user):
    """
    Send welcome email to newly verified user
    """
    try:
        # Email context
        context = {
            'user': user,
            'site_name': 'GoBarberly',
            'support_email': settings.DEFAULT_FROM_EMAIL,
        }
        
        # Render email templates
        subject = f"Welcome to {context['site_name']}!"
        html_message = render_to_string('emails/welcome.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Welcome email sent successfully to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
        return False


def send_password_changed_notification(user, request):
    """
    Send notification email when password is changed
    """
    try:
        # Email context
        context = {
            'user': user,
            'site_name': 'GoBarberly',
            'support_email': settings.DEFAULT_FROM_EMAIL,
            'ip_address': get_client_ip(request),
            'timestamp': timezone.now(),
        }
        
        # Render email templates
        subject = f"Password Changed - {context['site_name']}"
        html_message = render_to_string('emails/password_changed.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Password changed notification sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send password changed notification to {user.email}: {str(e)}")
        return False