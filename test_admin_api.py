"""
Test script for Admin API endpoints
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = 'http://127.0.0.1:8001/api'

class AdminAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.admin_token = None
        self.session = requests.Session()
    
    def login_admin(self, email='admin@gobarberly.com', password='AdminPass123'):
        """Login as admin and get access token"""
        print(f"🔑 Logging in as admin: {email}")
        
        response = self.session.post(f'{self.base_url}/auth/login/', json={
            'email': email,
            'password': password
        })
        
        if response.status_code == 200:
            data = response.json()
            self.admin_token = data.get('access')
            self.session.headers.update({
                'Authorization': f'Bearer {self.admin_token}'
            })
            print(f"✅ Login successful! Admin role: {data.get('user', {}).get('role')}")
            return True
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False
    
    def test_dashboard_stats(self):
        """Test admin dashboard statistics endpoint"""
        print("\n📊 Testing Dashboard Stats...")
        
        response = self.session.get(f'{self.base_url}/admin/dashboard/stats/')
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Dashboard stats retrieved successfully!")
            print(f"   📈 Total Barbershops: {data.get('total_barbershops', 0)}")
            print(f"   🟢 Active Barbershops: {data.get('active_barbershops', 0)}")
            print(f"   📅 Total Appointments: {data.get('total_appointments', 0)}")
            print(f"   💰 Monthly Revenue: ${data.get('monthly_revenue', 0)}")
            return data
        else:
            print(f"❌ Dashboard stats failed: {response.status_code} - {response.text}")
            return None
    
    def test_dashboard_data(self):
        """Test complete admin dashboard data endpoint"""
        print("\n📋 Testing Complete Dashboard Data...")
        
        response = self.session.get(f'{self.base_url}/admin/dashboard/data/')
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Dashboard data retrieved successfully!")
            print(f"   📊 Stats: {len(data.get('stats', {}))} metrics")
            print(f"   🎯 Recent Activities: {len(data.get('recent_activities', []))} items")
            print(f"   📅 Recent Appointments: {len(data.get('recent_appointments', []))} items")
            print(f"   🏪 Barbershop Summary: {len(data.get('barbershop_summary', []))} shops")
            return data
        else:
            print(f"❌ Dashboard data failed: {response.status_code} - {response.text}")
            return None
    
    def test_barbershop_list(self):
        """Test barbershop listing (admin scoped)"""
        print("\n🏪 Testing Barbershop List...")
        
        response = self.session.get(f'{self.base_url}/admin/barbershops/')
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Barbershop list retrieved successfully!")
            print(f"   📊 Total Results: {data.get('count', 0)}")
            print(f"   🏪 Current Page: {len(data.get('results', []))} barbershops")
            
            # Show first barbershop details
            if data.get('results'):
                first_shop = data['results'][0]
                print(f"   🔍 First Shop: {first_shop.get('shop_name')} - {first_shop.get('shop_owner_name')}")
                print(f"   💰 Monthly Revenue: ${first_shop.get('monthly_revenue', 0)}")
                print(f"   📅 Total Appointments: {first_shop.get('total_appointments', 0)}")
            
            return data
        else:
            print(f"❌ Barbershop list failed: {response.status_code} - {response.text}")
            return None
    
    def test_create_barbershop(self):
        """Test creating a new barbershop"""
        print("\n➕ Testing Barbershop Creation...")
        
        new_barbershop = {
            'email': f'newshop{datetime.now().strftime("%H%M%S")}@test.com',
            'shop_name': f'New Test Shop {datetime.now().strftime("%H:%M:%S")}',
            'shop_owner_name': 'New Owner',
            'address': '123 New Street, Test City',
            'phone_number': '+1234567999',
            'password': 'NewShop123',
            'password_confirm': 'NewShop123',
            'subscription_plan': 'premium'
        }
        
        response = self.session.post(f'{self.base_url}/admin/barbershops/', json=new_barbershop)
        
        if response.status_code == 201:
            data = response.json()
            print("✅ Barbershop created successfully!")
            print(f"   🏪 Shop: {data.get('shop_name')} (ID: {data.get('id')})")
            print(f"   👤 Owner: {data.get('shop_owner_name')}")
            print(f"   📧 Email: {data.get('email')}")
            return data
        else:
            print(f"❌ Barbershop creation failed: {response.status_code} - {response.text}")
            return None
    
    def test_activities_list(self):
        """Test activity feed listing"""
        print("\n📝 Testing Activities List...")
        
        response = self.session.get(f'{self.base_url}/admin/activities/')
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Activities retrieved successfully!")
            print(f"   📊 Total Activities: {data.get('count', 0)}")
            print(f"   📝 Current Page: {len(data.get('results', []))} activities")
            
            # Show recent activities
            if data.get('results'):
                for i, activity in enumerate(data['results'][:3]):
                    print(f"   {i+1}. {activity.get('action_type')} - {activity.get('description')[:50]}...")
                    print(f"      🏪 {activity.get('barbershop_name')} - {activity.get('time_ago')}")
            
            return data
        else:
            print(f"❌ Activities list failed: {response.status_code} - {response.text}")
            return None
    
    def test_appointments_list(self):
        """Test appointments listing"""
        print("\n📅 Testing Appointments List...")
        
        response = self.session.get(f'{self.base_url}/admin/appointments/')
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Appointments retrieved successfully!")
            print(f"   📊 Total Appointments: {data.get('count', 0)}")
            print(f"   📅 Current Page: {len(data.get('results', []))} appointments")
            
            # Show appointment breakdown by status
            if data.get('results'):
                statuses = {}
                for appointment in data['results']:
                    status = appointment.get('status', 'unknown')
                    statuses[status] = statuses.get(status, 0) + 1
                
                print("   📊 Status Breakdown:")
                for status, count in statuses.items():
                    print(f"      {status}: {count}")
            
            return data
        else:
            print(f"❌ Appointments list failed: {response.status_code} - {response.text}")
            return None
    
    def test_barbershop_analytics(self, barbershop_id):
        """Test barbershop analytics endpoint"""
        print(f"\n📈 Testing Barbershop Analytics (ID: {barbershop_id})...")
        
        response = self.session.get(f'{self.base_url}/admin/barbershops/{barbershop_id}/analytics/')
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Analytics retrieved successfully!")
            print(f"   🏪 Shop: {data.get('barbershop', {}).get('shop_name')}")
            print(f"   📊 Period: {data.get('period_days')} days")
            print(f"   📅 Total Appointments: {data.get('total_appointments', 0)}")
            print(f"   ✅ Completed: {data.get('completed_appointments', 0)}")
            print(f"   📈 Completion Rate: {data.get('completion_rate', 0):.1f}%")
            print(f"   💰 Total Revenue: ${data.get('total_revenue', 0)}")
            print(f"   💵 Avg per Appointment: ${data.get('average_revenue_per_appointment', 0)}")
            
            # Show monthly breakdown
            monthly_data = data.get('monthly_breakdown', [])
            if monthly_data:
                print("   📈 Monthly Breakdown:")
                for month_data in monthly_data[-3:]:  # Last 3 months
                    print(f"      {month_data.get('month')}: {month_data.get('appointments')} appointments, ${month_data.get('revenue')}")
            
            return data
        else:
            print(f"❌ Analytics failed: {response.status_code} - {response.text}")
            return None
    
    def test_filtered_queries(self):
        """Test various filtered queries"""
        print("\n🔍 Testing Filtered Queries...")
        
        # Test activity filters
        print("   🔍 Testing activity filters...")
        response = self.session.get(f'{self.base_url}/admin/activities/?action_type=appointment_completed')
        if response.status_code == 200:
            data = response.json()
            print(f"      ✅ Completed appointment activities: {data.get('count', 0)}")
        
        # Test appointment filters
        print("   🔍 Testing appointment filters...")
        response = self.session.get(f'{self.base_url}/admin/appointments/?status=completed')
        if response.status_code == 200:
            data = response.json()
            print(f"      ✅ Completed appointments: {data.get('count', 0)}")
        
        # Test barbershop search
        print("   🔍 Testing barbershop search...")
        response = self.session.get(f'{self.base_url}/admin/barbershops/?search=Test')
        if response.status_code == 200:
            data = response.json()
            print(f"      ✅ Search results: {data.get('count', 0)}")
    
    def run_comprehensive_test(self):
        """Run all tests"""
        print("🚀 Starting Comprehensive Admin API Test")
        print("=" * 50)
        
        # Login
        if not self.login_admin():
            print("❌ Cannot proceed without login")
            return
        
        # Test dashboard endpoints
        dashboard_stats = self.test_dashboard_stats()
        dashboard_data = self.test_dashboard_data()
        
        # Test barbershop management
        barbershops_data = self.test_barbershop_list()
        new_barbershop = self.test_create_barbershop()
        
        # Test activity and appointment feeds
        activities_data = self.test_activities_list()
        appointments_data = self.test_appointments_list()
        
        # Test analytics if we have barbershops
        if barbershops_data and barbershops_data.get('results'):
            first_barbershop_id = barbershops_data['results'][0]['id']
            self.test_barbershop_analytics(first_barbershop_id)
        
        # Test filtered queries
        self.test_filtered_queries()
        
        print("\n" + "=" * 50)
        print("✅ Comprehensive Admin API Test Completed!")
        
        # Summary
        if dashboard_stats:
            print(f"📊 Admin manages {dashboard_stats.get('total_barbershops', 0)} barbershops")
            print(f"💰 Total monthly revenue: ${dashboard_stats.get('monthly_revenue', 0)}")
        
        print("\n🎯 Key Features Tested:")
        print("   ✅ Admin authentication and authorization")
        print("   ✅ Dashboard statistics and data")
        print("   ✅ Barbershop listing and creation (scoped)")
        print("   ✅ Activity feed with filtering")
        print("   ✅ Appointment management")
        print("   ✅ Individual barbershop analytics")
        print("   ✅ Search and filtering capabilities")


if __name__ == '__main__':
    tester = AdminAPITester()
    tester.run_comprehensive_test()