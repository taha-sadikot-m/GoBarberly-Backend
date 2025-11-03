# GoBarberly Authentication API

A complete Django REST Framework authentication system with JWT tokens, email verification, and comprehensive user management.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Setup
Create a `.env` file in the backend directory:
```env
# Database Configuration
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432
SSL_MODE=disable

# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=noreply@gobarberly.com
```

### 3. Database Setup
Run the SQL setup script against your PostgreSQL database:
```bash
psql -U your_user -d your_database -f database_setup.sql
```

### 4. Django Setup
```bash
# Apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

## 📋 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/token/refresh/` - Refresh JWT token

### Email Verification
- `POST /api/auth/verify-email/` - Verify email address
- `POST /api/auth/resend-verification/` - Resend verification email

### Password Management
- `POST /api/auth/change-password/` - Change password (authenticated)
- `POST /api/auth/forgot-password/` - Request password reset
- `POST /api/auth/reset-password/` - Reset password with token

### User Profile
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/` - Update user profile
- `PATCH /api/auth/profile/` - Partial profile update

### Admin (Admin Only)
- `GET /api/auth/users/` - List all users

### API Documentation
- `GET /api/docs/` - Swagger UI documentation
- `GET /api/redoc/` - ReDoc documentation
- `GET /api/schema/` - OpenAPI schema

## 🔐 Authentication Flow

1. **Registration**: User registers → Email verification sent → User verifies email
2. **Login**: User logs in → Receives JWT tokens (access + refresh)
3. **API Access**: Include `Authorization: Bearer <access_token>` in headers
4. **Token Refresh**: Use refresh token to get new access token when expired

## 📝 API Response Format

All API endpoints return responses in this format:
```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... },
  "errors": null
}
```

## 🏗️ Project Structure

```
backend/
├── accounts/                   # Authentication app
│   ├── models.py              # User models and tokens
│   ├── serializers.py         # DRF serializers
│   ├── views.py               # API views
│   ├── urls.py                # URL routing
│   └── utils.py               # Email utilities
├── main/                      # Project settings
│   ├── settings.py            # Django settings
│   └── urls.py                # Main URL config
├── templates/
│   └── emails/                # Email templates
├── requirements.txt           # Python dependencies
├── database_setup.sql         # Database creation script
└── .env                       # Environment variables
```

## 🛡️ Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Validation**: Django's built-in password validators
- **Rate Limiting**: Protection against brute force attacks
- **Email Verification**: Mandatory email verification
- **CORS Configuration**: Proper cross-origin request handling
- **User Roles**: Role-based access control
- **Session Tracking**: Security monitoring and analytics
- **Token Expiration**: Automatic token refresh mechanism

## 🎨 User Roles

- `customer` - Regular customer (default)
- `barber` - Barber/stylist
- `shop_owner` - Barbershop owner
- `admin` - Administrator
- `super_admin` - Super administrator

## 📧 Email Templates

The system includes professional HTML email templates for:
- Email verification
- Password reset
- Welcome message
- Password change notification

## 🔧 Configuration

### JWT Token Settings
- Access token lifetime: 60 minutes
- Refresh token lifetime: 7 days
- Token rotation: Enabled
- Blacklist after rotation: Enabled

### Rate Limiting
- Registration: 5 attempts per minute
- Login: 10 attempts per minute
- Password reset: 3 attempts per minute
- Email verification: 3 attempts per minute

## 🚨 Error Handling

The API provides detailed error responses:
```json
{
  "success": false,
  "message": "Validation failed",
  "data": null,
  "errors": {
    "email": ["This field is required."],
    "password": ["This field is required."]
  }
}
```

## 📊 Database Schema

The system creates the following main tables:
- `accounts_user` - Custom user model
- `accounts_email_verification_token` - Email verification tokens
- `accounts_password_reset_token` - Password reset tokens
- `accounts_user_session` - User session tracking
- `accounts_user_login_history` - Login history and analytics

## 🧪 Testing

Test the API endpoints using tools like:
- Postman
- curl
- Django REST Framework browsable API
- Swagger UI (available at `/api/docs/`)

## 🔍 Monitoring

The system includes:
- Login history tracking
- User session monitoring
- Token usage analytics
- Security event logging

## 📈 Scalability

For production deployment:
1. Use environment variables for all configuration
2. Set up database connection pooling
3. Configure Redis for caching and rate limiting
4. Use a proper email service (SendGrid, Mailgun, etc.)
5. Set up monitoring and logging
6. Configure HTTPS and security headers

## 🐛 Troubleshooting

### Common Issues

1. **Email not sending**: Check email configuration in `.env`
2. **Database connection errors**: Verify database credentials
3. **Token errors**: Check JWT settings and secret key
4. **CORS issues**: Update CORS settings for your frontend URL

### Debug Mode

Set `DEBUG=True` in `.env` for development. Always set `DEBUG=False` in production.

## 📞 Support

For questions or issues, please check:
1. Django documentation
2. Django REST Framework documentation
3. Project issues/discussions

## 🔄 Updates

To update the system:
1. Pull latest changes
2. Install new dependencies: `pip install -r requirements.txt`
3. Run migrations: `python manage.py migrate`
4. Restart the server

---

**Note**: This is a development setup. For production, ensure proper security configurations, use HTTPS, and follow Django deployment best practices.