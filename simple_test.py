import requests
import json

def test_admin_api():
    base_url = 'http://127.0.0.1:8001/api'
    
    print("🔑 Testing Admin Login...")
    
    # Login as admin
    login_response = requests.post(f'{base_url}/auth/login/', json={
        'email': 'admin@gobarberly.com',
        'password': 'AdminPass123'
    })
    
    print(f"Login Status: {login_response.status_code}")
    print(f"Login Response: {login_response.text[:500]}")
    
    if login_response.status_code == 200:
        login_data = login_response.json()
        
        # The response has success, message, data structure
        data = login_data.get('data', {})
        token = data.get('access')
        user_info = data.get('user', {})
        
        headers = {'Authorization': f'Bearer {token}'}
        
        print("✅ Admin login successful!")
        print(f"User role: {user_info.get('role')}")
        print(f"User ID: {user_info.get('id')}")
        print(f"User email: {user_info.get('email')}")
        
        # Test dashboard stats
        print("\n📊 Testing Dashboard Stats...")
        stats_response = requests.get(f'{base_url}/admin/dashboard/stats/', headers=headers)
        print(f"Dashboard Stats Status: {stats_response.status_code}")
        
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
            print("✅ Dashboard stats retrieved!")
            print(f"Total Barbershops: {stats_data.get('total_barbershops')}")
            print(f"Active Barbershops: {stats_data.get('active_barbershops')}")
            print(f"Total Appointments: {stats_data.get('total_appointments')}")
            print(f"Monthly Revenue: ${stats_data.get('monthly_revenue')}")
        else:
            print(f"❌ Dashboard stats failed: {stats_response.text}")
        
        # Test barbershops list
        print("\n🏪 Testing Barbershops List...")
        barbershops_response = requests.get(f'{base_url}/admin/barbershops/', headers=headers)
        print(f"Barbershops List Status: {barbershops_response.status_code}")
        
        if barbershops_response.status_code == 200:
            barbershops_data = barbershops_response.json()
            print("✅ Barbershops list retrieved!")
            print(f"Total Barbershops: {barbershops_data.get('count')}")
            
            if barbershops_data.get('results'):
                first_shop = barbershops_data['results'][0]
                print(f"First Shop: {first_shop.get('shop_name')}")
                print(f"Shop Owner: {first_shop.get('shop_owner_name')}")
        else:
            print(f"❌ Barbershops list failed: {barbershops_response.text}")
        
        # Test activities
        print("\n📝 Testing Activities...")
        activities_response = requests.get(f'{base_url}/admin/activities/', headers=headers)
        print(f"Activities Status: {activities_response.status_code}")
        
        if activities_response.status_code == 200:
            activities_data = activities_response.json()
            print("✅ Activities retrieved!")
            print(f"Total Activities: {activities_data.get('count')}")
            
            if activities_data.get('results'):
                first_activity = activities_data['results'][0]
                print(f"Latest Activity: {first_activity.get('action_type')} - {first_activity.get('description')[:50]}...")
        else:
            print(f"❌ Activities failed: {activities_response.text}")
        
        # Test appointments
        print("\n📅 Testing Appointments...")
        appointments_response = requests.get(f'{base_url}/admin/appointments/', headers=headers)
        print(f"Appointments Status: {appointments_response.status_code}")
        
        if appointments_response.status_code == 200:
            appointments_data = appointments_response.json()
            print("✅ Appointments retrieved!")
            print(f"Total Appointments: {appointments_data.get('count')}")
        else:
            print(f"❌ Appointments failed: {appointments_response.text}")
        
        print("\n🎉 Admin API testing completed!")
        
    else:
        print(f"❌ Login failed: {login_response.text}")

if __name__ == '__main__':
    test_admin_api()