#!/usr/bin/env python
"""
Script to create a super admin user for testing
"""
import os
import sys
import django

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_super_admin():
    """Create a super admin user"""
    email = "19bmiit087@gmail.com"
    password = "Super@123"
    
    # Check if user already exists
    if User.objects.filter(email=email).exists():
        print(f"Super admin user already exists: {email}")
        user = User.objects.get(email=email)
        # Update password in case it changed
        user.set_password(password)
        user.role = "super_admin"
        user.is_staff = True
        user.is_superuser = True
        user.is_email_verified = True
        user.save()
        print(f"Super admin user updated with new credentials!")
    else:
        # Create super admin user
        user = User.objects.create_user(
            email=email,
            username=email,
            first_name="Super",
            last_name="Admin",
            role="super_admin",
            is_staff=True,
            is_superuser=True,
            is_email_verified=True
        )
        user.set_password(password)
        user.save()
        print(f"Super admin user created successfully!")
    
    print(f"Email: {email}")
    print(f"Password: {password}")
    print(f"Role: {user.role}")
    print(f"ID: {user.id}")
    print(f"Is Staff: {user.is_staff}")
    print(f"Is Superuser: {user.is_superuser}")
    print(f"Email Verified: {user.is_email_verified}")
    
    return user

if __name__ == "__main__":
    create_super_admin()