from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a Super Admin user with specified credentials'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default='19bmiit087@gmail.com',
            help='Email address for the super admin user'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='Super@123',
            help='Password for the super admin user'
        )
        parser.add_argument(
            '--first-name',
            type=str,
            default='Super',
            help='First name for the super admin user'
        )
        parser.add_argument(
            '--last-name',
            type=str,
            default='Admin',
            help='Last name for the super admin user'
        )

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']

        self.stdout.write(
            self.style.SUCCESS(f'Creating Super Admin user with email: {email}')
        )

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f'User with email {email} already exists!')
            )
            user = User.objects.get(email=email)
            
            # Update the user with super admin privileges
            user.set_password(password)
            user.first_name = first_name
            user.last_name = last_name
            user.role = "super_admin"
            user.is_staff = True
            user.is_superuser = True
            user.is_email_verified = True
            user.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Updated existing user to Super Admin!')
            )
        else:
            # Create new super admin user
            try:
                user = User.objects.create_user(
                    email=email,
                    username=email,
                    first_name=first_name,
                    last_name=last_name,
                    role="super_admin",
                    is_staff=True,
                    is_superuser=True,
                    is_email_verified=True
                )
                user.set_password(password)
                user.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'Super Admin user created successfully!')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating user: {str(e)}')
                )
                return

        # Display user information
        self.stdout.write(self.style.SUCCESS('\n=== Super Admin User Details ==='))
        self.stdout.write(f'Email: {user.email}')
        self.stdout.write(f'Password: {password}')
        self.stdout.write(f'Name: {user.first_name} {user.last_name}')
        self.stdout.write(f'Role: {user.role}')
        self.stdout.write(f'ID: {user.id}')
        self.stdout.write(f'Is Staff: {user.is_staff}')
        self.stdout.write(f'Is Superuser: {user.is_superuser}')
        self.stdout.write(f'Email Verified: {user.is_email_verified}')
        self.stdout.write(f'Date Created: {user.date_joined}')
        self.stdout.write(self.style.SUCCESS('\n✅ Super Admin is ready to use!'))
        
        # Instructions for testing
        self.stdout.write(self.style.WARNING('\n=== Next Steps ==='))
        self.stdout.write('1. Start your Django development server:')
        self.stdout.write('   python manage.py runserver')
        self.stdout.write('\n2. Test login at your frontend:')
        self.stdout.write('   http://localhost:3001/login')
        self.stdout.write(f'   Email: {email}')
        self.stdout.write(f'   Password: {password}')
        self.stdout.write('\n3. Verify Super Admin access:')
        self.stdout.write('   http://localhost:3001/super-admin')