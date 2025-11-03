"""
Django management command to verify email addresses for barbershop users created by admins
"""
from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = 'Verify email addresses for barbershop users created by admins/super admins'

    def handle(self, *args, **options):
        # Find barbershop users with unverified emails who were created by admins
        unverified_barbershops = User.objects.filter(
            role='barbershop',
            is_email_verified=False,
            created_by__isnull=False  # Must have been created by someone (admin/super admin)
        )
        
        count = unverified_barbershops.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('No unverified barbershop users found.')
            )
            return
        
        self.stdout.write(f'Found {count} unverified barbershop users created by admins.')
        
        # List users before updating
        for user in unverified_barbershops:
            creator_email = user.created_by.email if user.created_by else 'Unknown'
            self.stdout.write(f'- {user.email} (created by: {creator_email})')
        
        # Ask for confirmation
        confirm = input('Do you want to verify these barbershop users? (y/N): ')
        
        if confirm.lower() == 'y':
            # Update all unverified barbershop users
            updated_count = unverified_barbershops.update(is_email_verified=True)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully verified {updated_count} barbershop users.'
                )
            )
            
            # List updated users
            for user in User.objects.filter(
                role='barbershop',
                is_email_verified=True,
                created_by__isnull=False
            ):
                self.stdout.write(f'✓ {user.email} - Now verified')
        else:
            self.stdout.write('Operation cancelled.')