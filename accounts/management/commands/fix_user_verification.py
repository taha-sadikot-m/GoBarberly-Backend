from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Fix existing admin and barbershop users by verifying their emails'

    def handle(self, *args, **options):
        # Fix admin users
        admin_users = User.objects.filter(
            role='admin',
            is_email_verified=False
        )
        
        admin_count = admin_users.count()
        if admin_count > 0:
            admin_users.update(is_email_verified=True, is_active=True)
            self.stdout.write(
                self.style.SUCCESS(f'✅ Fixed {admin_count} admin user(s)')
            )
        else:
            self.stdout.write('ℹ️ No admin users need fixing')

        # Fix barbershop users
        barbershop_users = User.objects.filter(
            role='barbershop',
            is_email_verified=False
        )
        
        barbershop_count = barbershop_users.count()
        if barbershop_count > 0:
            barbershop_users.update(is_email_verified=True, is_active=True)
            self.stdout.write(
                self.style.SUCCESS(f'✅ Fixed {barbershop_count} barbershop user(s)')
            )
        else:
            self.stdout.write('ℹ️ No barbershop users need fixing')

        # Display status of all users
        self.stdout.write('\n=== User Status Summary ===')
        
        for role in ['super_admin', 'admin', 'barbershop']:
            users = User.objects.filter(role=role)
            verified_count = users.filter(is_email_verified=True).count()
            total_count = users.count()
            
            self.stdout.write(f'{role.title()}: {verified_count}/{total_count} email verified')
            
            if total_count > 0:
                for user in users:
                    status = "✅" if user.is_email_verified else "❌"
                    active = "🟢" if user.is_active else "🔴"
                    self.stdout.write(f'  {status}{active} {user.email} (ID: {user.id})')

        self.stdout.write(self.style.SUCCESS('\n🎉 All users should now be able to login!'))