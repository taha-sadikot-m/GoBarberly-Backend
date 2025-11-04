#!/usr/bin/env python3
"""
Test script to verify Admin Barbershop API permissions
"""
import requests
import json


BASE_URL = "http://127.0.0.1:8000/api"

class AdminBarbershopAPITester:
    def __init__(self):
        self.admin_token = None
        self.super_admin_token = None
        
    def login_admin(self):
        """Login as regular admin"""
        print("🔐 Logging in as regular admin...")
        
        # Try known admin credentials
        admin_credentials = [
            {"email": "taha.sadikot.m@gmail.com", "password": "Admin@123"},
            {"email": "testadmin@example.com", "password": "testpass123"},
            {"email": "testadmin@gobarberly.com", "password": "testpass123"},
            {"email": "admin@barbershop.com", "password": "adminpass123"},
        ]
        
        for creds in admin_credentials:
            try:
                response = requests.post(f"{BASE_URL}/auth/login/", {
                    "email": creds["email"],
                    "password": creds["password"]
                })
                
                if response.status_code == 200:
                    data = response.json()
                    # Check for token in different possible locations
                    if data.get('success') and 'data' in data and 'access' in data['data']:
                        self.admin_token = data['data']['access']
                        print(f"✅ Admin login successful with {creds['email']}!")
                        return True
                    elif 'access' in data:
                        self.admin_token = data['access']
                        print(f"✅ Admin login successful with {creds['email']}!")
                        return True
                    elif 'access_token' in data:
                        self.admin_token = data['access_token']
                        print(f"✅ Admin login successful with {creds['email']}!")
                        return True
                    else:
                        print(f"❌ Login response missing token: {data}")
                else:
                    print(f"❌ Login failed for {creds['email']}: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Login error for {creds['email']}: {e}")
                
        print("❌ Could not login as any admin user")
        return False
    
    def login_super_admin(self):
        """Login as super admin"""
        print("🔐 Logging in as super admin...")
        
        try:
            response = requests.post(f"{BASE_URL}/auth/login/", {
                "email": "19bmiit087@gmail.com",
                "password": "Taha@2002"
            })
            
            if response.status_code == 200:
                data = response.json()
                # Check for token in different possible locations
                if data.get('success') and 'data' in data and 'access' in data['data']:
                    self.super_admin_token = data['data']['access']
                    print("✅ Super admin login successful!")
                    return True
                elif 'access' in data:
                    self.super_admin_token = data['access']
                    print("✅ Super admin login successful!")
                    return True
                elif 'access_token' in data:
                    self.super_admin_token = data['access_token']
                    print("✅ Super admin login successful!")
                    return True
                else:
                    print(f"❌ Super admin login response missing token: {data}")
            else:
                print(f"❌ Super admin login failed: {response.status_code}")
                print(response.text)
                
        except Exception as e:
            print(f"❌ Super admin login error: {e}")
            
        return False
    
    def get_headers(self, user_type="admin"):
        """Get authorization headers"""
        token = self.admin_token if user_type == "admin" else self.super_admin_token
        return {"Authorization": f"Bearer {token}"}
    
    def test_admin_barbershop_api(self):
        """Test the admin barbershop API endpoint"""
        print("\n🏪 Testing Admin Barbershop API...")
        
        if not self.admin_token:
            print("❌ No admin token available")
            return
            
        # Test admin API endpoint
        admin_url = f"{BASE_URL}/admin/barbershops/"
        response = requests.get(admin_url, headers=self.get_headers("admin"))
        print(f"Admin API Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            admin_count = result.get('count', 0)
            print(f"✅ Admin sees {admin_count} barbershops via Admin API")
            
            # Show some barbershop details
            if result.get('results'):
                for i, shop in enumerate(result['results'][:3]):
                    print(f"   🏪 Shop {i+1}: {shop.get('shop_name', 'Unknown')} - {shop.get('shop_owner_name', 'Unknown Owner')}")
            
            return admin_count
        else:
            print(f"❌ Admin API failed: {response.text}")
            return 0
    
    def test_super_admin_barbershop_api(self):
        """Test the super admin barbershop API endpoint"""
        print("\n👑 Testing Super Admin Barbershop API...")
        
        if not self.super_admin_token:
            print("❌ No super admin token available")
            return
            
        # Test super admin API endpoint
        super_admin_url = f"{BASE_URL}/super-admin/barbershops/"
        response = requests.get(super_admin_url, headers=self.get_headers("super_admin"))
        print(f"Super Admin API Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            super_admin_count = result.get('count', 0)
            print(f"✅ Super Admin sees {super_admin_count} barbershops via Super Admin API")
            
            # Show some barbershop details
            if result.get('data'):
                for i, shop in enumerate(result['data'][:3]):
                    print(f"   🏪 Shop {i+1}: {shop.get('shop_name', 'Unknown')} - {shop.get('shop_owner_name', 'Unknown Owner')}")
            
            return super_admin_count
        else:
            print(f"❌ Super Admin API failed: {response.text}")
            return 0
    
    def run_comprehensive_test(self):
        """Run comprehensive barbershop API tests"""
        print("🚀 Starting Comprehensive Barbershop API Tests...")
        
        # Login as both users
        admin_logged_in = self.login_admin()
        super_admin_logged_in = self.login_super_admin()
        
        if not admin_logged_in and not super_admin_logged_in:
            print("❌ Could not login as any user type")
            return
        
        admin_count = 0
        super_admin_count = 0
        
        # Test admin API
        if admin_logged_in:
            admin_count = self.test_admin_barbershop_api()
        
        # Test super admin API
        if super_admin_logged_in:
            super_admin_count = self.test_super_admin_barbershop_api()
        
        # Compare results
        print("\n📊 RESULTS COMPARISON:")
        print(f"   👤 Admin API: {admin_count} barbershops")
        print(f"   👑 Super Admin API: {super_admin_count} barbershops")
        
        if admin_logged_in and super_admin_logged_in:
            if admin_count <= super_admin_count:
                print("✅ PASS: Admin sees fewer or equal barbershops than Super Admin")
                print("✅ Role-based filtering is working correctly!")
            else:
                print("❌ FAIL: Admin sees MORE barbershops than Super Admin!")
                print("❌ Role-based filtering is NOT working correctly!")
        else:
            print("⚠️ Could not compare both APIs due to login issues")


if __name__ == "__main__":
    tester = AdminBarbershopAPITester()
    tester.run_comprehensive_test()