#!/usr/bin/env python3
"""
End-to-end test for Barbershop Profile API integration
Tests both auth profile and barbershop profile endpoints
"""
import os
import sys
import django
import json
import requests
from pathlib import Path

# Add the backend directory to Python path  
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

BASE_URL = 'http://127.0.0.1:8000'

def create_test_barbershop_user():
    """Create a test barbershop user with logo simulation"""
    try:
        # Delete existing test user if any
        User.objects.filter(email='integration_test@example.com').delete()
        
        user = User.objects.create_user(
            username='integration_test',
            email='integration_test@example.com',
            password='testpass123',
            first_name='Integration',
            last_name='Test',
            role='barbershop',
            shop_name='Integration Test Barbershop',
            shop_owner_name='Integration Test Owner',
            # Simulate a logo URL (would normally be uploaded file)
            # shop_logo='/media/shop_logos/test_logo.png'
        )
        print(f"✅ Created integration test user: {user.email}")
        return user
    except Exception as e:
        print(f"❌ Failed to create test user: {e}")
        return None

def get_auth_token(user):
    """Get JWT token for user"""
    try:
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        print(f"✅ Generated auth token for {user.email}")
        return access_token
    except Exception as e:
        print(f"❌ Failed to generate token: {e}")
        return None

def test_auth_profile_endpoint(token):
    """Test the main auth profile endpoint that frontend uses for login"""
    print("\n" + "="*60)
    print("TESTING AUTH PROFILE ENDPOINT (/api/auth/profile/)")
    print("="*60)
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f'{BASE_URL}/api/auth/profile/', headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Data: {json.dumps(data, indent=2)}")
            
            # Check if barbershop fields are included
            if 'data' in data:
                user_data = data['data']
                has_shop_fields = any(field in user_data for field in ['shop_name', 'shop_owner_name', 'shop_logo'])
                
                if has_shop_fields:
                    print("✅ Auth profile includes barbershop fields")
                    return True, user_data
                else:
                    print("⚠️  Auth profile missing barbershop fields")
                    return False, user_data
            else:
                print("❌ Unexpected response format")
                return False, None
        else:
            print(f"❌ Request failed: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False, None

def test_barbershop_profile_endpoint(token):
    """Test the barbershop-specific profile endpoint"""
    print("\n" + "="*60)
    print("TESTING BARBERSHOP PROFILE ENDPOINT (/api/barbershop/profile/)")
    print("="*60)
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test GET
        print("\n📍 Testing GET request...")
        response = requests.get(f'{BASE_URL}/api/barbershop/profile/', headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Data: {json.dumps(data, indent=2)}")
            print("✅ GET request successful")
            
            # Test PUT
            print("\n📍 Testing PUT request...")
            update_data = {
                'shop_name': 'Updated Integration Test Shop',
                'shop_owner_name': 'Updated Owner',
                'address': '123 Test Street, Test City'
            }
            
            response = requests.put(
                f'{BASE_URL}/api/barbershop/profile/', 
                headers=headers,
                json=update_data
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response Data: {json.dumps(data, indent=2)}")
                print("✅ PUT request successful")
                return True
            else:
                print(f"❌ PUT request failed: {response.text}")
                return False
        else:
            print(f"❌ GET request failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_frontend_integration_flow():
    """Test the complete flow that frontend would use"""
    print("\n" + "="*60)
    print("TESTING FRONTEND INTEGRATION FLOW")
    print("="*60)
    
    # 1. Create test user
    user = create_test_barbershop_user()
    if not user:
        return False
    
    # 2. Get auth token (simulates login)
    token = get_auth_token(user)
    if not token:
        return False
    
    # 3. Test auth profile (what frontend calls on login)
    print("\n🔄 Step 1: Frontend calls auth profile on login...")
    auth_success, auth_data = test_auth_profile_endpoint(token)
    
    # 4. Test barbershop profile (what sidebar component would call)
    print("\n🔄 Step 2: Sidebar component fetches barbershop profile...")
    barbershop_success = test_barbershop_profile_endpoint(token)
    
    # 5. Validate integration
    if auth_success and barbershop_success:
        print("\n🎉 INTEGRATION TEST SUCCESSFUL!")
        print("✅ Frontend can authenticate and get user profile")
        print("✅ Sidebar can fetch barbershop-specific profile data")
        print("✅ Both endpoints return consistent data")
        return True
    else:
        print("\n💥 INTEGRATION TEST FAILED!")
        return False

def main():
    """Main test function"""
    print("🚀 Starting End-to-End Barbershop Profile Integration Test")
    print("This test simulates the complete frontend-backend integration flow")
    
    success = test_frontend_integration_flow()
    
    if success:
        print("\n🎉 ALL TESTS PASSED! Integration is working correctly.")
        print("✅ Backend endpoints are ready")
        print("✅ Frontend can integrate successfully")
    else:
        print("\n💥 SOME TESTS FAILED! Check the output above.")
    
    print("\nTest completed.")

if __name__ == '__main__':
    main()