#!/usr/bin/env python
"""
Test script for Super Admin API endpoints

This script tests all super admin API endpoints including:
- Dashboard statistics
- Admin management (list, detail, search)
- Barbershop management (list, detail, search, by admin)
- Archive data (inactive admins/barbershops)
- System logs and statistics
- Search and pagination functionality
- Creation of new admins and barbershops

Usage:
  python test_super_admin_api.py              # Run all tests
  python test_super_admin_api.py dashboard    # Run specific test
  python test_super_admin_api.py admin_detail # Run admin detail test

Available test names:
  dashboard, admin_list, barbershop_list, admin_detail, barbershop_detail,
  barbershop_by_admin, search, pagination, archive, logs, statistics,
  create_admin, create_barbershop
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
        self.admin_token = None  # For testing admin access
    
    def login(self, user_type="super_admin"):
        """Login as super admin or admin and get access token"""
        url = f"{AUTH_URL}/login/"
        
        if user_type == "super_admin":
            data = {
                "email": "19bmiit087@gmail.com",
                "password": "Super@123"
            }
        else:  # admin
            data = {
                "email": "testadmin@gobarberly.com",
                "password": "TestAdmin123!"
            }
        
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                if user_type == "super_admin":
                    self.access_token = result['data']['access']
                    self.refresh_token = result['data']['refresh']
                else:
                    self.admin_token = result['data']['access']
                print(f"✅ {user_type} login successful!")
                return True
        
        print(f"❌ {user_type} login failed!")
        print(response.text)
        return False
    
    def get_headers(self, user_type="super_admin"):
        """Get authorization headers"""
        token = self.access_token if user_type == "super_admin" else self.admin_token
        return {
            'Authorization': f'Bearer {token}',
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
    
    def test_get_admin_detail(self):
        """Test fetching specific admin data"""
        print("\n👤 Testing Get Admin Detail...")
        
        # First get list of admins to get an ID
        list_url = f"{SUPER_ADMIN_URL}/admins/"
        list_response = requests.get(list_url, headers=self.get_headers())
        
        if list_response.status_code == 200:
            admin_list = list_response.json()
            if admin_list.get('data') and len(admin_list['data']) > 0:
                admin_id = admin_list['data'][0]['id']
                
                # Now get specific admin detail
                detail_url = f"{SUPER_ADMIN_URL}/admins/{admin_id}/"
                response = requests.get(detail_url, headers=self.get_headers())
                print(f"Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print("✅ Admin detail retrieved successfully!")
                    admin_data = result.get('data', {})
                    
                    # Handle different possible field names
                    name = admin_data.get('name') or f"{admin_data.get('first_name', '')} {admin_data.get('last_name', '')}".strip()
                    email = admin_data.get('email', 'N/A')
                    is_active = admin_data.get('is_active', 'N/A')
                    
                    print(f"Admin: {name} ({email})")
                    print(f"Status: {is_active}")
                    print("Full admin data:", json.dumps(admin_data, indent=2))
                    return admin_id
                else:
                    print("❌ Admin detail fetch failed!")
                    print(response.text)
            else:
                print("⚠️ No admins found to test detail fetch")
                return None
        else:
            print("❌ Could not get admin list for detail test")
            return None
    
    def test_get_barbershop_detail(self):
        """Test fetching specific barbershop data"""
        print("\n🏪 Testing Get Barbershop Detail...")
        
        # First get list of barbershops to get an ID
        list_url = f"{SUPER_ADMIN_URL}/barbershops/"
        list_response = requests.get(list_url, headers=self.get_headers())
        
        if list_response.status_code == 200:
            barbershop_list = list_response.json()
            if barbershop_list.get('data') and len(barbershop_list['data']) > 0:
                barbershop_id = barbershop_list['data'][0]['id']
                
                # Now get specific barbershop detail
                detail_url = f"{SUPER_ADMIN_URL}/barbershops/{barbershop_id}/"
                response = requests.get(detail_url, headers=self.get_headers())
                print(f"Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print("✅ Barbershop detail retrieved successfully!")
                    shop_data = result.get('data', {})
                    
                    # Handle different possible field names
                    shop_name = shop_data.get('shop_name') or shop_data.get('name', 'N/A')
                    email = shop_data.get('email', 'N/A')
                    owner_name = shop_data.get('shop_owner_name') or shop_data.get('owner_name', 'N/A')
                    is_active = shop_data.get('is_active', 'N/A')
                    subscription = shop_data.get('subscription_plan', 'N/A')
                    
                    print(f"Shop: {shop_name} ({email})")
                    print(f"Owner: {owner_name}")
                    print(f"Status: {is_active}")
                    print(f"Subscription: {subscription}")
                    print("Full barbershop data:", json.dumps(shop_data, indent=2))
                    return barbershop_id
                else:
                    print("❌ Barbershop detail fetch failed!")
                    print(response.text)
            else:
                print("⚠️ No barbershops found to test detail fetch")
                return None
        else:
            print("❌ Could not get barbershop list for detail test")
            return None
    
    def test_get_barbershop_by_admin(self):
        """Test fetching barbershops assigned to specific admin"""
        print("\n🔗 Testing Get Barbershops by Admin...")
        
        # First get an admin ID
        admin_id = self.test_get_admin_detail()
        if admin_id:
            url = f"{SUPER_ADMIN_URL}/admins/{admin_id}/barbershops/"
            response = requests.get(url, headers=self.get_headers())
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Admin's barbershops retrieved successfully!")
                print(f"Admin has {result.get('count', 0)} barbershops assigned")
                barbershops = result.get('data', [])
                if barbershops and len(barbershops) > 0:
                    print("Admin's assigned barbershops:")
                    for shop in barbershops[:3]:  # Show first 3
                        shop_name = shop.get('shop_name', shop.get('name', 'N/A'))
                        email = shop.get('email', 'N/A')
                        print(f"  - {shop_name} ({email})")
                else:
                    print("No barbershops assigned to this admin")
            else:
                print("❌ Admin's barbershops fetch failed!")
                print(response.text)
        else:
            print("⚠️ Skipping admin barbershops test - no admin ID available")
    
    def test_archive_data(self):
        """Test fetching archive data"""
        print("\n📦 Testing Archive Data...")
        
        # Test archived admins
        print("  📂 Testing Archived Admins...")
        archived_admins_url = f"{SUPER_ADMIN_URL}/admins/?status=inactive"
        response = requests.get(archived_admins_url, headers=self.get_headers())
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Found {result.get('count', 0)} archived admins")
        else:
            print("  ❌ Archived admins fetch failed!")
            print(response.text)
        
        # Test archived barbershops
        print("  📂 Testing Archived Barbershops...")
        archived_shops_url = f"{SUPER_ADMIN_URL}/barbershops/?status=inactive"
        response = requests.get(archived_shops_url, headers=self.get_headers())
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Found {result.get('count', 0)} archived barbershops")
        else:
            print("  ❌ Archived barbershops fetch failed!")
            print(response.text)
    
    def test_system_logs(self):
        """Test fetching system logs/activity data"""
        print("\n📋 Testing System Logs...")
        
        # Test recent activity logs
        logs_url = f"{SUPER_ADMIN_URL}/logs/"
        response = requests.get(logs_url, headers=self.get_headers())
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ System logs retrieved successfully!")
            print(f"Found {len(result.get('data', []))} log entries")
            
            # Show recent logs
            if result.get('data'):
                print("Recent activities:")
                for log in result['data'][:5]:  # Show first 5
                    print(f"  - {log.get('action', 'Unknown')} by {log.get('user', 'System')}")
        elif response.status_code == 404:
            print("⚠️ System logs endpoint not available")
        else:
            print("❌ System logs fetch failed!")
            print(response.text)
    
    def test_statistics_data(self):
        """Test fetching detailed statistics and reports"""
        print("\n📊 Testing Detailed Statistics...")
        
        # Test monthly statistics
        monthly_stats_url = f"{SUPER_ADMIN_URL}/statistics/monthly/"
        response = requests.get(monthly_stats_url, headers=self.get_headers())
        print(f"Monthly Stats Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Monthly statistics retrieved successfully!")
            print(f"Data points: {len(result.get('data', []))}")
        elif response.status_code == 404:
            print("⚠️ Monthly statistics endpoint not available")
        else:
            print("❌ Monthly statistics fetch failed!")
        
        # Test user growth data
        growth_url = f"{SUPER_ADMIN_URL}/statistics/growth/"
        response = requests.get(growth_url, headers=self.get_headers())
        print(f"Growth Stats Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Growth statistics retrieved successfully!")
        elif response.status_code == 404:
            print("⚠️ Growth statistics endpoint not available")
        else:
            print("❌ Growth statistics fetch failed!")
    
    def test_barbershop_access_permissions(self):
        """Test that Super Admin sees all barbershops while Admin sees only their own"""
        print("\n🔐 Testing Barbershop Access Permissions...")
        
        # Test Super Admin access
        print("  👑 Testing Super Admin Access...")
        url = f"{SUPER_ADMIN_URL}/barbershops/"
        response = requests.get(url, headers=self.get_headers("super_admin"))
        print(f"  Super Admin Status Code: {response.status_code}")
        
        super_admin_count = 0
        if response.status_code == 200:
            result = response.json()
            super_admin_count = result.get('count', 0)
            print(f"  ✅ Super Admin sees {super_admin_count} barbershops")
        else:
            print("  ❌ Super Admin barbershop access failed!")
            print(response.text)
        
        # Test Admin access (if admin token is available)
        if self.admin_token:
            print("  👤 Testing Admin Access...")
            response = requests.get(url, headers=self.get_headers("admin"))
            print(f"  Admin Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                admin_count = result.get('count', 0)
                print(f"  ✅ Admin sees {admin_count} barbershops")
                
                # Verify that admin sees fewer or equal barbershops than super admin
                if admin_count <= super_admin_count:
                    print(f"  ✅ Permission filtering working correctly!")
                    print(f"     Super Admin: {super_admin_count} barbershops")
                    print(f"     Admin: {admin_count} barbershops")
                else:
                    print(f"  ❌ Permission filtering NOT working!")
                    print(f"     Admin sees MORE barbershops than Super Admin!")
            else:
                print("  ❌ Admin barbershop access failed!")
                print(response.text)
        else:
            print("  ⚠️ Admin token not available, skipping admin access test")
    
    def test_search_functionality(self):
        """Test search functionality for admins and barbershops"""
        print("\n🔍 Testing Search Functionality...")
        
        # Test admin search
        print("  🔎 Testing Admin Search...")
        search_term = "@"  # Search for emails containing @
        admin_search_url = f"{SUPER_ADMIN_URL}/admins/?search={search_term}"
        response = requests.get(admin_search_url, headers=self.get_headers())
        print(f"  Admin Search Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Found {result.get('count', 0)} admins matching '{search_term}'")
        else:
            print("  ❌ Admin search failed!")
            print(response.text)
        
        # Test barbershop search
        print("  🔎 Testing Barbershop Search...")
        shop_search_url = f"{SUPER_ADMIN_URL}/barbershops/?search=shop"
        response = requests.get(shop_search_url, headers=self.get_headers())
        print(f"  Barbershop Search Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Found {result.get('count', 0)} barbershops matching 'shop'")
        else:
            print("  ❌ Barbershop search failed!")
            print(response.text)
    
    def test_pagination(self):
        """Test pagination functionality"""
        print("\n📄 Testing Pagination...")
        
        # Test admin pagination
        print("  📖 Testing Admin Pagination...")
        paginated_url = f"{SUPER_ADMIN_URL}/admins/?page=1&page_size=5"
        response = requests.get(paginated_url, headers=self.get_headers())
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Page 1 retrieved successfully!")
            print(f"  Results: {len(result.get('data', []))} items")
            print(f"  Total: {result.get('count', 0)} items")
            
            # Test next page if available
            if result.get('next'):
                print("  📖 Testing Next Page...")
                next_response = requests.get(result['next'], headers=self.get_headers())
                if next_response.status_code == 200:
                    print("  ✅ Next page retrieved successfully!")
                else:
                    print("  ❌ Next page failed!")
        else:
            print("  ❌ Pagination test failed!")
            print(response.text)
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Super Admin API Tests...")
        
        if not self.login():
            return
        
        # Test basic endpoints
        self.test_dashboard_stats()
        self.test_admin_list()
        self.test_barbershop_list()
        
        # Test detailed data fetching
        self.test_get_admin_detail()
        self.test_get_barbershop_detail()
        self.test_get_barbershop_by_admin()
        
        # Test role-based permissions
        self.test_barbershop_access_permissions()
        
        # Test search and pagination
        self.test_search_functionality()
        self.test_pagination()
        
        # Test archive and system data
        self.test_archive_data()
        self.test_system_logs()
        self.test_statistics_data()
        
        # Test creation endpoints
        self.test_create_admin()
        self.test_create_barbershop()
        
        print("\n🎉 All tests completed!")
    
    def run_specific_test(self, test_name):
        """Run a specific test by name"""
        print(f"🚀 Starting {test_name} test...")
        
        if not self.login():
            return
        
        test_methods = {
            'dashboard': self.test_dashboard_stats,
            'admin_list': self.test_admin_list,
            'barbershop_list': self.test_barbershop_list,
            'admin_detail': self.test_get_admin_detail,
            'barbershop_detail': self.test_get_barbershop_detail,
            'barbershop_by_admin': self.test_get_barbershop_by_admin,
            'permissions': self.test_barbershop_access_permissions,
            'search': self.test_search_functionality,
            'pagination': self.test_pagination,
            'archive': self.test_archive_data,
            'logs': self.test_system_logs,
            'statistics': self.test_statistics_data,
            'create_admin': self.test_create_admin,
            'create_barbershop': self.test_create_barbershop,
        }
        
        if test_name in test_methods:
            test_methods[test_name]()
            print(f"\n✅ {test_name} test completed!")
        else:
            print(f"❌ Test '{test_name}' not found!")
            print("Available tests:", ", ".join(test_methods.keys()))

if __name__ == "__main__":
    import sys
    
    tester = SuperAdminAPITest()
    
    # Check if specific test is requested
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        tester.run_specific_test(test_name)
    else:
        tester.run_all_tests()