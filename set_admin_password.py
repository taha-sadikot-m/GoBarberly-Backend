#!/usr/bin/env python
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from django.contrib.auth.hashers import make_password
from accounts.models import User

def set_admin_password():
    """Set a known password for the admin user"""
    try:
        # Find the admin user
        admin_user = User.objects.filter(role='admin', email='taha.sadikot.m@gmail.com').first()
        
        if admin_user:
            # Set a known password
            new_password = "AdminTest123!"
            admin_user.password = make_password(new_password)
            admin_user.save()
            
            print(f"✅ Password set for admin: {admin_user.email}")
            print(f"📧 Email: {admin_user.email}")
            print(f"🔑 Password: {new_password}")
            print(f"👤 Role: {admin_user.role}")
            print(f"🆔 ID: {admin_user.id}")
            
            return new_password
        else:
            print("❌ Admin user not found!")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    set_admin_password()