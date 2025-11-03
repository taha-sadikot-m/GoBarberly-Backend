#!/usr/bin/env python3
"""
Test script for Barbershop Profile API endpoint
"""
import os
import sys
import django
import json
from pathlib import Path

# Add the backend directory to Python path  
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

try:
    django.setup()
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

# Now import Django modules
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def create_test_barbershop_user():
    """Create a test barbershop user"""
    try:
        # Delete existing test user if any
        User.objects.filter(email='test_barbershop@example.com').delete()
        
        user = User.objects.create_user(
            username='test_barbershop',
            email='test_barbershop@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Barbershop',
            role='barbershop',
            shop_name='Test Barbershop',
            shop_owner_name='Test Owner'
        )
        print(f"✅ Created test barbershop user: {user.email}")
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

def test_barbershop_profile_endpoint():
    """Test the barbershop profile endpoint"""
    print("\n" + "="*50)
    print("TESTING BARBERSHOP PROFILE ENDPOINT")
    print("="*50)
    
    # Create test user
    user = create_test_barbershop_user()
    if not user:
        return False
    
    # Get auth token
    token = get_auth_token(user)
    if not token:
        return False
    
    # Create API client with forced HOST header
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    
    try:
        # Test GET request
        print("\n📍 Testing GET /api/barbershop/profile/")
        response = client.get('/api/barbershop/profile/', HTTP_HOST='127.0.0.1:8000')
        
        print(f"Status Code: {response.status_code}")
        
        # Handle response data safely
        response_data = None
        try:
            if hasattr(response, 'data'):
                response_data = response.data
            elif hasattr(response, 'json'):
                response_data = response.json()
            else:
                response_data = {'content': response.content.decode()}
        except:
            response_data = {'raw_content': str(response.content)}
            
        print(f"Response Data: {json.dumps(response_data, indent=2, default=str)}")
        
        if response.status_code == 200:
            print("✅ GET request successful")
            
            # Test PUT request (update profile)
            print("\n📍 Testing PUT /api/barbershop/profile/")
            update_data = {
                'shop_name': 'Updated Barbershop Name',
                'shop_owner_name': 'Updated Owner Name'
            }
            
            response = client.put('/api/barbershop/profile/', update_data, format='json', HTTP_HOST='127.0.0.1:8000')
            print(f"Status Code: {response.status_code}")
            
            try:
                if hasattr(response, 'data'):
                    response_data = response.data
                elif hasattr(response, 'json'):
                    response_data = response.json()
                else:
                    response_data = {'content': response.content.decode()}
            except:
                response_data = {'raw_content': str(response.content)}
                
            print(f"Response Data: {json.dumps(response_data, indent=2, default=str)}")
            
            if response.status_code == 200:
                print("✅ PUT request successful")
                return True
            else:
                print(f"❌ PUT request failed")
                return False
        else:
            print(f"❌ GET request failed")
            return False
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("Starting Barbershop Profile API Tests...")
    
    success = test_barbershop_profile_endpoint()
    
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n💥 Some tests failed!")
    
    print("\nTest completed.")

if __name__ == '__main__':
    main()