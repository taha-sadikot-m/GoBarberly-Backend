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
    
    # Test sales API
    headers = {'Authorization': f'Bearer {token}'}
    sales_url = 'http://127.0.0.1:8000/api/barbershop/sales/'
    
    sales_response = requests.get(sales_url, headers=headers)
    print(f'Sales API Status: {sales_response.status_code}')
    if sales_response.status_code <= 299:
        sales_data = sales_response.json()
        print(f'Sales Count: {len(sales_data.get("results", []))}')
        print(f'Data Structure: {list(sales_data.keys())}')
        if sales_data.get('results'):
            print(f'First Sale Keys: {list(sales_data["results"][0].keys())}')
            print(f'First Sale: {sales_data["results"][0]}')
    else:
        print(f'Error: {sales_response.text}')
        
    # Test creating a sale
    print('\n--- Testing Sale Creation ---')
    create_data = {
        'customer_name': 'Frontend Test Customer',
        'service': 'Beard Trim',
        'barber_name': 'Frontend Barber',
        'amount': 200,
        'payment_method': 'Paytm'
    }
    
    create_response = requests.post(sales_url, headers=headers, json=create_data)
    print(f'Create Sale Status: {create_response.status_code}')
    if create_response.status_code <= 299:
        print(f'Created Sale: {create_response.json()}')
    else:
        print(f'Create Error: {create_response.text}')
        
else:
    print(f'Login failed: {response.status_code} - {response.text}')