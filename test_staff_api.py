import requests
import json

# Login to get fresh token
login_url = 'http://127.0.0.1:8000/api/auth/login/'
login_data = {
    'email': 'freshbarbershop@test.com',
    'password': 'test123'
}

response = requests.post(login_url, data=login_data)
print(f'Login response: {response.status_code} - {response.text}')
if response.status_code == 200:
    response_data = response.json()
    token = response_data.get('access') or response_data.get('data', {}).get('access')
    if token:
        print(f'Token: {token[:50]}...')
    else:
        print(f'No token found in response: {response_data}')
        exit()
        
    # Test staff API
    headers = {'Authorization': f'Bearer {token}'}
    staff_url = 'http://127.0.0.1:8000/api/barbershop/staff/'
    
    staff_response = requests.get(staff_url, headers=headers)
    print(f'Staff API Status: {staff_response.status_code}')
    if staff_response.status_code <= 299:
        staff_data = staff_response.json()
        print(f'Staff Count: {len(staff_data.get("results", []))}')
        print(f'Data Structure: {list(staff_data.keys())}')
        if staff_data.get('results'):
            print(f'First Staff Keys: {list(staff_data["results"][0].keys())}')
            print(f'First Staff: {staff_data["results"][0]}')
    else:
        print(f'Error: {staff_response.text}')
        
    # Test creating a staff member
    print('\n--- Testing Staff Creation ---')
    create_data = {
        'name': 'Frontend Test Staff',
        'role': 'Barber',
        'phone': '9876543210',
        'email': 'teststaff@example.com',
        'status': 'Active',
        'schedule': 'Mon-Fri 9AM-6PM',
        'salary': 25000
    }
    
    create_response = requests.post(staff_url, headers=headers, json=create_data)
    print(f'Create Staff Status: {create_response.status_code}')
    if create_response.status_code <= 299:
        print(f'Created Staff: {create_response.json()}')
    else:
        print(f'Create Error: {create_response.text}')
        
else:
    print(f'Login failed: {response.status_code} - {response.text}')