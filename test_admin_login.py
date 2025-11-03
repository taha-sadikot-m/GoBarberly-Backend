#!/usr/bin/env python
"""
Test script to verify admin login functionality
"""
import os
import sys
import django
import requests
import json

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def test_admin_login():
    """Test admin login functionality"""
    print("🧪 Testing Admin Login Fix")
    print("=" * 50)
    
    # Check existing admin users
    admin_users = User.objects.filter(role='admin')
    print(f"Found {admin_users.count()} admin user(s)")
    
    if admin_users.count() == 0:
        print("❌ No admin users found. Create one first through Super Admin dashboard.")
        return
    
    # Test each admin user
    for admin in admin_users:
        print(f"\n👤 Testing admin: {admin.email}")
        print(f"   Email Verified: {admin.is_email_verified}")
        print(f"   Is Active: {admin.is_active}")
        print(f"   Role: {admin.role}")
        print(f"   Created by: {admin.created_by.email if admin.created_by else 'N/A'}")
        
        # Test login via API (assuming backend is running on port 8000)
        try:
            login_data = {
                'email': admin.email,
                'password': 'admin123'  # Default password for created admins
            }
            
            response = requests.post(
                'http://localhost:8000/api/auth/login/',
                json=login_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"   ✅ Login successful!")
                    user_info = data.get('data', {}).get('user', {})
                    print(f"   👤 User role: {user_info.get('role')}")
                    print(f"   📧 Email verified: {user_info.get('is_email_verified')}")
                else:
                    print(f"   ❌ Login failed: {data.get('message')}")
            else:
                error_data = response.json()
                print(f"   ❌ Login failed (HTTP {response.status_code}): {error_data.get('message')}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ⚠️ Could not connect to backend API. Make sure Django server is running.")
        except Exception as e:
            print(f"   ❌ Error testing login: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print("1. If login fails with 'Email address is not verified', run: python manage.py fix_user_verification")
    print("2. If login fails with 'Invalid credentials', check the password used when creating the admin")
    print("3. Make sure Django backend is running: python manage.py runserver")

if __name__ == "__main__":
    test_admin_login()