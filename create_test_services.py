#!/usr/bin/env python
"""Create test services for the barbershop system."""
import os
import sys
import django

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
django.setup()

from django.contrib.auth import get_user_model
from barbershop_operations.models import Barbershop, BarbershopService
from accounts.models import CustomUser

User = get_user_model()

def create_test_services():
    """Create test services for existing barbershops."""
    try:
        # Get or create a test barbershop
        barbershop = Barbershop.objects.first()
        if not barbershop:
            # Create a test user first
            user = User.objects.filter(email='admin@example.com').first()
            if not user:
                user = User.objects.create_user(
                    email='admin@example.com',
                    password='admin123',
                    first_name='Admin',
                    last_name='User',
                    role='super_admin'
                )
                print(f"Created test user: {user.email}")
            
            barbershop = Barbershop.objects.create(
                name='Test Barbershop',
                owner=user,
                address='123 Test Street',
                phone='1234567890',
                email='test@barbershop.com'
            )
            print(f"Created test barbershop: {barbershop.name}")
        
        # Create test services
        services_data = [
            {
                'name': 'Classic Haircut',
                'price': 30.00,
                'description': 'Professional haircut with styling',
                'duration_minutes': 45
            },
            {
                'name': 'Beard Trim',
                'price': 15.00,
                'description': 'Beard trimming and shaping',
                'duration_minutes': 20
            },
            {
                'name': 'Hot Towel Shave',
                'price': 25.00,
                'description': 'Traditional hot towel shave',
                'duration_minutes': 30
            },
            {
                'name': 'Hair Wash & Style',
                'price': 20.00,
                'description': 'Hair washing and styling service',
                'duration_minutes': 25
            },
            {
                'name': 'Combo (Cut + Beard)',
                'price': 40.00,
                'description': 'Haircut and beard trim combo',
                'duration_minutes': 60
            }
        ]
        
        created_services = []
        for service_data in services_data:
            service, created = BarbershopService.objects.get_or_create(
                barbershop=barbershop,
                name=service_data['name'],
                defaults=service_data
            )
            if created:
                created_services.append(service)
                print(f"Created service: {service.name} - ${service.price}")
            else:
                print(f"Service already exists: {service.name}")
        
        print(f"\nTotal services for {barbershop.name}: {BarbershopService.objects.filter(barbershop=barbershop).count()}")
        
        # Display all services
        print("\nAll services:")
        for service in BarbershopService.objects.filter(barbershop=barbershop):
            print(f"- {service.name}: ${service.price} ({service.duration_minutes} min)")
            
    except Exception as e:
        print(f"Error creating test services: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_test_services()