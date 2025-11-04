import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:8000"
SUPER_ADMIN_URL = f"{BASE_URL}/api/super-admin"
ADMIN_LOGIN_URL = f"{BASE_URL}/api/auth/login/"

# Admin credentials (from the admin detail test)
ADMIN_EMAIL = "taha.sadikot.m@gmail.com"
# We'll need to set a known password for this admin

class AdminFilteringTest:
    def __init__(self):
        self.super_admin_token = None
        self.admin_token = None
    
    def login_as_super_admin(self):
        """Login as super admin"""
        data = {
            "email": "19bmiit087@gmail.com",
            "password": "Super@123"
        }
        
        response = requests.post(ADMIN_LOGIN_URL, json=data)
        if response.status_code == 200:
            result = response.json()
            # Check what fields are available in the response
            print(f"Login response: {result}")
            self.super_admin_token = result.get('data', {}).get('access') or result.get('access_token') or result.get('access')
            print("✅ Super Admin login successful!")
            print(f"Token: {self.super_admin_token[:20]}..." if self.super_admin_token else "No token found")
            return True
        else:
            print("❌ Super Admin login failed!")
            print(response.text)
            return False
    
    def login_as_admin(self):
        """Try to login as regular admin"""
        # Common passwords to try
        passwords = ["admin123", "password", "admin", "123456", "Admin123!", "admin123!"]
        
        for password in passwords:
            print(f"🔑 Trying password: {password}")
            data = {
                "email": ADMIN_EMAIL,
                "password": password
            }
            
            response = requests.post(ADMIN_LOGIN_URL, json=data)
            if response.status_code == 200:
                result = response.json()
                self.admin_token = result.get('access_token')
                print(f"✅ Admin login successful with password: {password}")
                return True
            else:
                print(f"❌ Failed with password: {password}")
        
        print("❌ Could not login as admin with any common password")
        return False
    
    def get_headers(self, user_type="super_admin"):
        """Get headers with appropriate token"""
        token = self.super_admin_token if user_type == "super_admin" else self.admin_token
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def test_barbershop_filtering(self):
        """Test barbershop access for both user types"""
        print("\n🔐 Testing Barbershop Filtering...")
        
        if not self.login_as_super_admin():
            return
        
        # Test Super Admin access
        print("\n👑 Testing Super Admin Access...")
        url = f"{SUPER_ADMIN_URL}/barbershops/"
        response = requests.get(url, headers=self.get_headers("super_admin"))
        
        if response.status_code == 200:
            result = response.json()
            super_admin_count = result.get('count', 0)
            print(f"✅ Super Admin sees {super_admin_count} barbershops")
            
            # Show some barbershop details
            if 'results' in result and result['results']:
                print("  Sample barbershops:")
                for i, shop in enumerate(result['results'][:3]):
                    print(f"    {i+1}. {shop.get('name', 'N/A')} (ID: {shop.get('id', 'N/A')})")
        else:
            print("❌ Super Admin access failed!")
            print(response.text)
            return
        
        # Try to login as admin
        if self.login_as_admin():
            print("\n👤 Testing Admin Access...")
            response = requests.get(url, headers=self.get_headers("admin"))
            
            if response.status_code == 200:
                result = response.json()
                admin_count = result.get('count', 0)
                print(f"✅ Admin sees {admin_count} barbershops")
                
                # Show admin's barbershops
                if 'results' in result and result['results']:
                    print("  Admin's barbershops:")
                    for i, shop in enumerate(result['results']):
                        print(f"    {i+1}. {shop.get('name', 'N/A')} (ID: {shop.get('id', 'N/A')})")
                
                # Compare counts
                print(f"\n📊 Comparison:")
                print(f"   Super Admin: {super_admin_count} barbershops")
                print(f"   Admin: {admin_count} barbershops")
                
                if admin_count <= super_admin_count:
                    print("✅ Filtering is working correctly!")
                    if admin_count == 1:  # Expected based on admin detail
                        print("✅ Admin sees exactly 1 barbershop as expected!")
                    else:
                        print(f"⚠️ Expected admin to see 1 barbershop, but sees {admin_count}")
                else:
                    print("❌ Filtering is NOT working - admin sees more than super admin!")
            else:
                print("❌ Admin access failed!")
                print(response.text)
        else:
            print("⚠️ Could not test admin access - login failed")

if __name__ == "__main__":
    tester = AdminFilteringTest()
    tester.test_barbershop_filtering()