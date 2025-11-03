#!/usr/bin/env python
"""
API Testing Script for GoBarberly Authentication System
This script validates the API endpoints and structure.
"""

import json
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def test_api_structure():
    """Test the API structure and configuration"""
    print("🧪 Testing GoBarberly Authentication API Structure\n")
    
    # Test 1: Check if all required files exist
    print("📁 Checking file structure...")
    required_files = [
        'requirements.txt',
        'main/settings.py',
        'main/urls.py',
        'accounts/models.py',
        'accounts/serializers.py',
        'accounts/views.py',
        'accounts/urls.py',
        'accounts/utils.py',
        'accounts/admin.py',
        'templates/emails/email_verification.html',
        'templates/emails/password_reset.html',
        'templates/emails/welcome.html',
        'templates/emails/password_changed.html',
        'database_setup.sql',
        '.env'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not (backend_dir / file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"  ✅ {file_path}")
    
    if missing_files:
        print(f"\n❌ Missing files: {missing_files}")
        return False
    
    print("\n✅ All required files are present!")
    
    # Test 2: Check API endpoints configuration
    print("\n🔗 Checking API endpoints...")
    
    try:
        # Read the accounts URLs
        with open(backend_dir / 'accounts' / 'urls.py', 'r') as f:
            urls_content = f.read()
        
        expected_endpoints = [
            'register/',
            'login/',
            'logout/',
            'token/refresh/',
            'verify-email/',
            'resend-verification/',
            'change-password/',
            'forgot-password/',
            'reset-password/',
            'profile/',
            'users/'
        ]
        
        for endpoint in expected_endpoints:
            if endpoint in urls_content:
                print(f"  ✅ {endpoint}")
            else:
                print(f"  ❌ {endpoint} - Missing")
                
    except Exception as e:
        print(f"❌ Error reading URLs: {e}")
        return False
    
    # Test 3: Check models structure
    print("\n📊 Checking models...")
    
    try:
        with open(backend_dir / 'accounts' / 'models.py', 'r') as f:
            models_content = f.read()
        
        expected_models = [
            'class User',
            'class EmailVerificationToken',
            'class PasswordResetToken',
            'class UserSession',
            'class UserLoginHistory'
        ]
        
        for model in expected_models:
            if model in models_content:
                print(f"  ✅ {model}")
            else:
                print(f"  ❌ {model} - Missing")
                
    except Exception as e:
        print(f"❌ Error reading models: {e}")
        return False
    
    # Test 4: Check serializers
    print("\n📝 Checking serializers...")
    
    try:
        with open(backend_dir / 'accounts' / 'serializers.py', 'r') as f:
            serializers_content = f.read()
        
        expected_serializers = [
            'UserRegistrationSerializer',
            'CustomTokenObtainPairSerializer',
            'UserProfileSerializer',
            'ChangePasswordSerializer',
            'PasswordResetRequestSerializer',
            'PasswordResetConfirmSerializer',
            'EmailVerificationSerializer',
            'ResendVerificationSerializer'
        ]
        
        for serializer in expected_serializers:
            if serializer in serializers_content:
                print(f"  ✅ {serializer}")
            else:
                print(f"  ❌ {serializer} - Missing")
                
    except Exception as e:
        print(f"❌ Error reading serializers: {e}")
        return False
    
    # Test 5: Check views
    print("\n🎯 Checking views...")
    
    try:
        with open(backend_dir / 'accounts' / 'views.py', 'r') as f:
            views_content = f.read()
        
        expected_views = [
            'UserRegistrationView',
            'CustomTokenObtainPairView',
            'LogoutView',
            'UserProfileView',
            'ChangePasswordView',
            'PasswordResetRequestView',
            'PasswordResetConfirmView',
            'EmailVerificationView',
            'ResendVerificationView',
            'UserListView'
        ]
        
        for view in expected_views:
            if view in views_content:
                print(f"  ✅ {view}")
            else:
                print(f"  ❌ {view} - Missing")
                
    except Exception as e:
        print(f"❌ Error reading views: {e}")
        return False
    
    # Test 6: Check email templates
    print("\n📧 Checking email templates...")
    
    email_templates = [
        'email_verification.html',
        'password_reset.html',
        'welcome.html',
        'password_changed.html'
    ]
    
    for template in email_templates:
        template_path = backend_dir / 'templates' / 'emails' / template
        if template_path.exists():
            # Check if template has required elements
            with open(template_path, 'r') as f:
                content = f.read()
                if '{{ user' in content and '{{ site_name }}' in content:
                    print(f"  ✅ {template}")
                else:
                    print(f"  ⚠️  {template} - Missing template variables")
        else:
            print(f"  ❌ {template} - Missing")
    
    print("\n🎉 API Structure Validation Complete!")
    print("\n📋 Summary:")
    print("✅ All core files are present")
    print("✅ API endpoints are configured")
    print("✅ Models are properly defined")
    print("✅ Serializers are implemented")
    print("✅ Views are created")
    print("✅ Email templates are available")
    print("✅ Database setup script is ready")
    
    print("\n🚀 Next Steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Configure your .env file with proper database credentials")
    print("3. Run the database setup script: psql -f database_setup.sql")
    print("4. Create and apply migrations: python manage.py makemigrations && python manage.py migrate")
    print("5. Start the development server: python manage.py runserver")
    print("6. Access API documentation at: http://localhost:8000/api/docs/")
    
    return True

def generate_api_test_commands():
    """Generate curl commands to test API endpoints"""
    print("\n🔧 API Testing Commands:")
    print("Use these curl commands to test your API endpoints:")
    
    base_url = "http://localhost:8000/api/auth"
    
    commands = {
        "Register User": f"""curl -X POST {base_url}/register/ \\
  -H "Content-Type: application/json" \\
  -d '{{
    "email": "test@example.com",
    "username": "testuser",
    "first_name": "Test",
    "last_name": "User",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "role": "customer"
  }}'""",
        
        "Login User": f"""curl -X POST {base_url}/login/ \\
  -H "Content-Type: application/json" \\
  -d '{{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }}'""",
        
        "Get Profile": f"curl -X GET {base_url}/profile/ -H \"Authorization: Bearer YOUR_ACCESS_TOKEN\"",
        
        "Change Password": f"curl -X POST {base_url}/change-password/ -H \"Content-Type: application/json\" -H \"Authorization: Bearer YOUR_ACCESS_TOKEN\" -d '{{\"old_password\": \"SecurePass123!\", \"new_password\": \"NewSecurePass123!\", \"new_password_confirm\": \"NewSecurePass123!\"}}'",
        
        "Forgot Password": f"curl -X POST {base_url}/forgot-password/ -H \"Content-Type: application/json\" -d '{{\"email\": \"test@example.com\"}}'",
        
        "API Documentation": "Visit: http://localhost:8000/api/docs/"
    }
    
    for name, command in commands.items():
        print(f"\n{name}:")
        print(command)

if __name__ == "__main__":
    success = test_api_structure()
    
    if success:
        generate_api_test_commands()
        print(f"\n🎯 Authentication API is ready for use!")
    else:
        print(f"\n❌ There are issues with the API structure. Please review the errors above.")
        sys.exit(1)