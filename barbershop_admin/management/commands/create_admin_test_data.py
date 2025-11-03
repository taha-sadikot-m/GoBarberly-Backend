"""
Management command to create admin test data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import random

from barbershop_admin.models import Activity, Appointment
from super_admin.models import Subscription


User = get_user_model()


class Command(BaseCommand):
    help = 'Create test data for admin functionality'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--admin-email',
            type=str,
            default='admin@test.com',
            help='Email for the test admin user'
        )
        parser.add_argument(
            '--admin-password',
            type=str,
            default='admin123',
            help='Password for the test admin user'
        )
        parser.add_argument(
            '--barbershops',
            type=int,
            default=3,
            help='Number of barbershops to create'
        )
        parser.add_argument(
            '--appointments',
            type=int,
            default=20,
            help='Number of appointments to create per barbershop'
        )
    
    def handle(self, *args, **options):
        self.stdout.write('Creating admin test data...')
        
        # Create admin user
        admin = self.create_admin_user(
            options['admin_email'],
            options['admin_password']
        )
        
        # Create barbershops
        barbershops = self.create_barbershops(admin, options['barbershops'])
        
        # Create appointments and activities
        self.create_appointments_and_activities(barbershops, options['appointments'])
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created test data with {len(barbershops)} barbershops '
                f'and {options["appointments"]} appointments each'
            )
        )
    
    def create_admin_user(self, email, password):
        """Create or get admin user"""
        admin, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'role': 'admin',
                'first_name': 'Test',
                'last_name': 'Admin',
                'is_active': True,
                'is_email_verified': True
            }
        )
        
        if created:
            admin.set_password(password)
            admin.save()
            self.stdout.write(f'Created admin user: {email}')
        else:
            self.stdout.write(f'Using existing admin user: {email}')
        
        return admin
    
    def create_barbershops(self, admin, count):
        """Create barbershop users"""
        barbershops = []
        
        for i in range(count):
            email = f'barbershop{i+1}@test.com'
            shop_name = f'Test Barbershop {i+1}'
            
            barbershop, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email,
                    'role': 'barbershop',
                    'shop_name': shop_name,
                    'shop_owner_name': f'Owner {i+1}',
                    'address': f'{100 + i*10} Main St, Test City',
                    'phone_number': f'+1234567890{i}',
                    'first_name': f'Owner',
                    'last_name': f'{i+1}',
                    'is_active': True,
                    'is_email_verified': True,
                    'created_by': admin
                }
            )
            
            if created:
                barbershop.set_password('barbershop123')
                barbershop.save()
                
                # Create subscription
                Subscription.objects.get_or_create(
                    user=barbershop,
                    defaults={
                        'plan': random.choice(['basic', 'premium', 'enterprise']),
                        'status': 'active'
                    }
                )
                
                # Create initial activity
                Activity.objects.create(
                    barbershop=barbershop,
                    action_type='profile_updated',
                    description=f'Barbershop account created by {admin.get_full_name()}',
                    metadata={
                        'created_by': admin.id,
                        'setup': True
                    }
                )
                
                self.stdout.write(f'Created barbershop: {shop_name}')
            
            barbershops.append(barbershop)
        
        return barbershops
    
    def create_appointments_and_activities(self, barbershops, appointments_per_shop):
        """Create appointments and activities for barbershops"""
        services = [
            'Haircut', 'Beard Trim', 'Hair Wash', 'Styling', 'Color',
            'Hot Towel Shave', 'Mustache Trim', 'Hair Treatment'
        ]
        
        statuses = ['scheduled', 'completed', 'cancelled', 'no_show']
        status_weights = [0.3, 0.5, 0.15, 0.05]  # More completed appointments
        
        for barbershop in barbershops:
            self.stdout.write(f'Creating appointments for {barbershop.shop_name}...')
            
            for j in range(appointments_per_shop):
                # Random date within last 60 days or next 30 days
                base_date = timezone.now() - timedelta(days=60)
                random_days = random.randint(0, 90)
                appointment_date = base_date + timedelta(days=random_days)
                
                status = random.choices(statuses, weights=status_weights)[0]
                service = random.choice(services)
                amount = Decimal(str(random.randint(20, 100)))
                
                appointment = Appointment.objects.create(
                    barbershop=barbershop,
                    customer_name=f'Customer {j+1}',
                    customer_email=f'customer{j+1}@test.com',
                    customer_phone=f'+1555000{j:04d}',
                    service=service,
                    amount=amount,
                    appointment_date=appointment_date,
                    duration=random.randint(30, 120),
                    status=status,
                    notes=f'Test appointment {j+1} for {service}'
                )
                
                # Create related activity
                if status == 'completed':
                    Activity.objects.create(
                        barbershop=barbershop,
                        action_type='appointment_completed',
                        description=f'Appointment completed: {service} for {appointment.customer_name}',
                        amount=amount,
                        timestamp=appointment_date + timedelta(hours=1),
                        metadata={
                            'appointment_id': appointment.id,
                            'service': service,
                            'customer': appointment.customer_name
                        }
                    )
                elif status == 'cancelled':
                    Activity.objects.create(
                        barbershop=barbershop,
                        action_type='appointment_cancelled',
                        description=f'Appointment cancelled: {service} for {appointment.customer_name}',
                        timestamp=appointment_date - timedelta(hours=2),
                        metadata={
                            'appointment_id': appointment.id,
                            'service': service,
                            'customer': appointment.customer_name
                        }
                    )
            
            # Add some general activities
            for k in range(5):
                activity_date = timezone.now() - timedelta(days=random.randint(1, 30))
                
                activity_types = [
                    ('profile_updated', 'Profile information updated'),
                    ('subscription_updated', 'Subscription plan updated'),
                    ('login', 'User logged in to system'),
                    ('settings_changed', 'Account settings modified')
                ]
                
                activity_type, description = random.choice(activity_types)
                
                Activity.objects.create(
                    barbershop=barbershop,
                    action_type=activity_type,
                    description=description,
                    timestamp=activity_date,
                    metadata={
                        'auto_generated': True,
                        'test_data': True
                    }
                )
        
        self.stdout.write('Created appointments and activities successfully')