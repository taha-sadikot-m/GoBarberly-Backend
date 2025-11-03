#!/usr/bin/env python
"""
Check barbershop ownership
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def check_barbershop_ownership():
    """Check which admin owns which barbershops"""
    print("=== ALL USERS ===")
    for user in User.objects.all():
        print(f"{user.email} - {user.role} - Active: {user.is_active}")

    print("\n=== BARBERSHOPS AND THEIR CREATORS ===")
    barbershops = User.objects.filter(role='barbershop')
    for shop in barbershops:
        creator = shop.created_by.email if shop.created_by else 'Unknown'
        print(f"{shop.shop_name} ({shop.email}) - Created by: {creator}")
    
    print(f"\nTotal barbershops: {barbershops.count()}")

if __name__ == '__main__':
    check_barbershop_ownership()