#!/usr/bin/env python
"""
Create sample data for testing barbershop management
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
django.setup()

from django.contrib.auth import get_user_model
from super_admin.models import Subscription
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

def create_sample_data():
    """Create sample admin and barbershop users"""
    print("Creating sample data...")
    
    # Create admin user
    admin_user, created = User.objects.get_or_create(
        email='admin@barbershop.com',
        defaults={
            'username': 'admin@barbershop.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'role': 'admin',
            'is_active': True,
            'is_email_verified': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print(f"✅ Created admin user: {admin_user.email}")
    else:
        print(f"ℹ️  Admin user already exists: {admin_user.email}")
    
    # Create sample barbershops
    barbershops_data = [
        {
            'email': 'shop1@barbershop.com',
            'shop_name': 'The Classic Barbershop',
            'shop_owner_name': 'John Smith',
            'address': '123 Main Street, Downtown',
            'phone_number': '+1-555-0101',
        },
        {
            'email': 'shop2@barbershop.com',
            'shop_name': 'Modern Cuts & Shaves',
            'shop_owner_name': 'Mike Johnson',
            'address': '456 Oak Avenue, Midtown',
            'phone_number': '+1-555-0102',
        },
        {
            'email': 'shop3@barbershop.com',
            'shop_name': 'Gentleman\'s Corner',
            'shop_owner_name': 'David Wilson',
            'address': '789 Pine Road, Uptown',
            'phone_number': '+1-555-0103',
        },
        {
            'email': 'shop4@barbershop.com',
            'shop_name': 'Vintage Barbershop',
            'shop_owner_name': 'Robert Brown',
            'address': '321 Elm Street, Old Town',
            'phone_number': '+1-555-0104',
        },
        {
            'email': 'shop5@barbershop.com',
            'shop_name': 'Style & Shave Co.',
            'shop_owner_name': 'Christopher Davis',
            'address': '654 Maple Drive, New District',
            'phone_number': '+1-555-0105',
        },
        {
            'email': 'shop6@barbershop.com',
            'shop_name': 'The Barber\'s Den',
            'shop_owner_name': 'James Miller',
            'address': '987 Cedar Lane, West Side',
            'phone_number': '+1-555-0106',
        },
        {
            'email': 'shop7@barbershop.com',
            'shop_name': 'Sharp Cuts Barbershop',
            'shop_owner_name': 'Thomas Anderson',
            'address': '147 Birch Street, East End',
            'phone_number': '+1-555-0107',
        },
        {
            'email': 'shop8@barbershop.com',
            'shop_name': 'Professional Grooming',
            'shop_owner_name': 'William Taylor',
            'address': '258 Walnut Avenue, South District',
            'phone_number': '+1-555-0108',
        }
    ]
    
    created_count = 0
    for shop_data in barbershops_data:
        barbershop, created = User.objects.get_or_create(
            email=shop_data['email'],
            defaults={
                'username': shop_data['email'],
                'first_name': shop_data['shop_owner_name'].split()[0],
                'last_name': ' '.join(shop_data['shop_owner_name'].split()[1:]),
                'role': 'barbershop',
                'shop_name': shop_data['shop_name'],
                'shop_owner_name': shop_data['shop_owner_name'],
                'address': shop_data['address'],
                'phone_number': shop_data['phone_number'],
                'is_active': True,
                'is_email_verified': True,
                'created_by': admin_user
            }
        )
        
        if created:
            barbershop.set_password('barbershop123')
            barbershop.save()
            created_count += 1
            
            # Create subscription for each barbershop
            subscription, sub_created = Subscription.objects.get_or_create(
                user=barbershop,
                defaults={
                    'plan': 'basic',
                    'status': 'active',
                    'started_at': timezone.now(),
                    'expires_at': timezone.now() + timedelta(days=30),
                }
            )
            
            print(f"✅ Created barbershop: {barbershop.shop_name} ({barbershop.email})")
        else:
            print(f"ℹ️  Barbershop already exists: {barbershop.shop_name} ({barbershop.email})")
        
        # Ensure email is verified for all barbershops
        if not barbershop.is_email_verified:
            barbershop.is_email_verified = True
            barbershop.save(update_fields=['is_email_verified'])
            print(f"   📧 Email verified for {barbershop.email}")
    
    # Also verify admin email
    if not admin_user.is_email_verified:
        admin_user.is_email_verified = True
        admin_user.save(update_fields=['is_email_verified'])
        print(f"📧 Email verified for admin: {admin_user.email}")
    
    total_shops = User.objects.filter(role='barbershop', created_by=admin_user).count()
    print(f"\n🎉 Sample data creation complete!")
    print(f"📊 Total barbershops for admin '{admin_user.email}': {total_shops}")
    print(f"🆕 Created {created_count} new barbershops")
    
    print(f"\n🔐 Login credentials:")
    print(f"   Admin: admin@barbershop.com / admin123")
    print(f"   Any barbershop: [email from list above] / barbershop123")

if __name__ == '__main__':
    create_sample_data()