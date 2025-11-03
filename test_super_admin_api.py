#!/usr/bin/env python
"""
Test script for Super Admin API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"
AUTH_URL = f"{BASE_URL}/api/auth"
SUPER_ADMIN_URL = f"{BASE_URL}/api/super-admin"

class SuperAdminAPITest:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
    
    def login(self):
        """Login as super admin and get access token"""
        url = f"{AUTH_URL}/login/"
        data = {
            "email": "superadmin@gobarberly.com",
            "password": "SuperAdmin123!"
        }
        
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                self.access_token = result['data']['access']
                self.refresh_token = result['data']['refresh']
                print("✅ Login successful!")
                return True
        
        print("❌ Login failed!")
        print(response.text)
        return False
    
    def get_headers(self):
        """Get authorization headers"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def test_dashboard_stats(self):
        """Test dashboard statistics endpoint"""
        print("\n📊 Testing Dashboard Stats...")
        url = f"{SUPER_ADMIN_URL}/dashboard/stats/"
        
        response = requests.get(url, headers=self.get_headers())
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Dashboard stats retrieved successfully!")
            print(json.dumps(result, indent=2))
        else:
            print("❌ Dashboard stats failed!")
            print(response.text)
    
    def test_admin_list(self):
        """Test admin list endpoint"""
        print("\n👥 Testing Admin List...")
        url = f"{SUPER_ADMIN_URL}/admins/"
        
        response = requests.get(url, headers=self.get_headers())
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Admin list retrieved successfully!")
            print(f"Total admins: {result.get('count', 0)}")
        else:
            print("❌ Admin list failed!")
            print(response.text)
    
    def test_barbershop_list(self):
        """Test barbershop list endpoint"""
        print("\n✂️ Testing Barbershop List...")
        url = f"{SUPER_ADMIN_URL}/barbershops/"
        
        response = requests.get(url, headers=self.get_headers())
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Barbershop list retrieved successfully!")
            print(f"Total barbershops: {result.get('count', 0)}")
        else:
            print("❌ Barbershop list failed!")
            print(response.text)
    
    def test_create_admin(self):
        """Test creating a new admin"""
        print("\n➕ Testing Create Admin...")
        url = f"{SUPER_ADMIN_URL}/admins/"
        
        data = {
            "email": "testadmin@gobarberly.com",
            "first_name": "Test",
            "last_name": "Admin",
            "password": "TestAdmin123!",
            "password_confirm": "TestAdmin123!"
        }
        
        response = requests.post(url, json=data, headers=self.get_headers())
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Admin created successfully!")
            print(f"Admin ID: {result['data']['id']}")
            return result['data']['id']
        else:
            print("❌ Admin creation failed!")
            print(response.text)
            return None
    
    def test_create_barbershop(self):
        """Test creating a new barbershop"""
        print("\n🏪 Testing Create Barbershop...")
        url = f"{SUPER_ADMIN_URL}/barbershops/"
        
        data = {
            "email": "testshop@gobarberly.com",
            "shop_name": "Test Barbershop",
            "shop_owner_name": "Test Owner",
            "address": "123 Test St, Test City",
            "phone_number": "+1-555-TEST",
            "password": "TestShop123!",
            "password_confirm": "TestShop123!",
            "subscription_plan": "basic"
        }
        
        response = requests.post(url, json=data, headers=self.get_headers())
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Barbershop created successfully!")
            print(f"Barbershop ID: {result['data']['id']}")
            return result['data']['id']
        else:
            print("❌ Barbershop creation failed!")
            print(response.text)
            return None
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Super Admin API Tests...")
        
        if not self.login():
            return
        
        # Test all endpoints
        self.test_dashboard_stats()
        self.test_admin_list()
        self.test_barbershop_list()
        self.test_create_admin()
        self.test_create_barbershop()
        
        print("\n🎉 All tests completed!")

if __name__ == "__main__":
    tester = SuperAdminAPITest()
    tester.run_all_tests()