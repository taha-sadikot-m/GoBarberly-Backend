# GoBarberly Authentication API Documentation

## 📋 Complete API Reference

**Base URL:** `http://localhost:8000/api/auth/`

**Content-Type:** `application/json` (for all POST/PUT/PATCH requests)

---

## 🔐 Authentication Endpoints

### 1. **User Registration**
**Endpoint:** `POST /api/auth/register/`  
**Authentication:** Not required  
**Description:** Register a new user account

#### Request Body:
```json
{
  "email": "user@example.com",
  "username": "testuser",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "role": "customer"
}
```

#### Required Fields:
- `email` (string) - Valid email address, must be unique
- `username` (string) - Alphanumeric with underscores, must be unique
- `first_name` (string) - User's first name
- `last_name` (string) - User's last name
- `password` (string) - Minimum 8 characters
- `password_confirm` (string) - Must match password

#### Optional Fields:
- `phone_number` (string) - Valid phone format (e.g., +1234567890)
- `role` (string) - One of: `customer`, `barber`, `shop_owner`, `admin`, `super_admin` (default: `customer`)

#### Success Response (201):
```json
{
  "success": true,
  "message": "Registration successful. Please check your email for verification link.",
  "data": {
    "user_id": 1,
    "email": "user@example.com",
    "username": "testuser"
  },
  "errors": null
}
```

#### Error Response (400):
```json
{
  "success": false,
  "message": "Registration failed. Please check the provided information.",
  "data": null,
  "errors": {
    "email": ["A user with this email already exists."],
    "password": ["This password is too common."]
  }
}
```

---

### 2. **User Login**
**Endpoint:** `POST /api/auth/login/`  
**Authentication:** Not required  
**Description:** Authenticate user and receive JWT tokens

#### Request Body:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

#### Required Fields:
- `email` (string) - User's email address
- `password` (string) - User's password

#### Success Response (200):
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "username": "testuser",
      "first_name": "John",
      "last_name": "Doe",
      "role": "customer",
      "is_email_verified": true,
      "is_profile_complete": false
    }
  },
  "errors": null
}
```

#### Error Response (401):
```json
{
  "success": false,
  "message": "Invalid credentials",
  "data": null,
  "errors": {
    "non_field_errors": ["No active account found with the given credentials"]
  }
}
```

---

### 3. **User Logout**
**Endpoint:** `POST /api/auth/logout/`  
**Authentication:** Required (Bearer Token)  
**Description:** Logout user and blacklist refresh token

#### Headers:
```
Authorization: Bearer <access_token>
```

#### Request Body:
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Required Fields:
- `refresh_token` (string) - The refresh token to blacklist

#### Success Response (200):
```json
{
  "success": true,
  "message": "Successfully logged out",
  "data": null,
  "errors": null
}
```

---

### 4. **Refresh JWT Token**
**Endpoint:** `POST /api/auth/token/refresh/`  
**Authentication:** Not required  
**Description:** Get new access token using refresh token

#### Request Body:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Required Fields:
- `refresh` (string) - Valid refresh token

#### Success Response (200):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## 📧 Email Verification Endpoints

### 5. **Verify Email**
**Endpoint:** `GET /api/auth/verify-email/` or `POST /api/auth/verify-email/`  
**Authentication:** Not required  
**Description:** Verify user's email address with token

#### Method 1: GET (Email Link Click)
**URL:** `/api/auth/verify-email/?token=550e8400-e29b-41d4-a716-446655440000`

#### Query Parameters:
- `token` (UUID string) - Email verification token received via email

#### Method 2: POST (API Call)
#### Request Body:
```json
{
  "token": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### Required Fields:
- `token` (UUID string) - Email verification token received via email

#### Success Response (200):
```json
{
  "success": true,
  "message": "Email verified successfully! You can now log in to your account.",
  "data": {
    "user_email": "user@example.com",
    "redirect_url": "/login"
  },
  "errors": null
}
```

#### Error Response (400):
```json
{
  "success": false,
  "message": "Email verification failed",
  "data": null,
  "errors": {
    "token": ["Invalid or expired verification token."]
  }
}
```

---

### 6. **Resend Verification Email**
**Endpoint:** `POST /api/auth/resend-verification/`  
**Authentication:** Not required  
**Description:** Resend email verification link

#### Request Body:
```json
{
  "email": "user@example.com"
}
```

#### Required Fields:
- `email` (string) - User's email address

#### Success Response (200):
```json
{
  "success": true,
  "message": "Verification email sent successfully",
  "data": null,
  "errors": null
}
```

---

## 🔑 Password Management Endpoints

### 7. **Change Password** (Authenticated)
**Endpoint:** `POST /api/auth/change-password/`  
**Authentication:** Required (Bearer Token)  
**Description:** Change password for authenticated user

#### Headers:
```
Authorization: Bearer <access_token>
```

#### Request Body:
```json
{
  "old_password": "SecurePass123!",
  "new_password": "NewSecurePass456!",
  "new_password_confirm": "NewSecurePass456!"
}
```

#### Required Fields:
- `old_password` (string) - Current password
- `new_password` (string) - New password (minimum 8 characters)
- `new_password_confirm` (string) - Must match new_password

#### Success Response (200):
```json
{
  "success": true,
  "message": "Password changed successfully",
  "data": null,
  "errors": null
}
```

#### Error Response (400):
```json
{
  "success": false,
  "message": "Password change failed",
  "data": null,
  "errors": {
    "old_password": ["Old password is incorrect."],
    "new_password": ["This password is too common."]
  }
}
```

---

### 8. **Forgot Password**
**Endpoint:** `POST /api/auth/forgot-password/`  
**Authentication:** Not required  
**Description:** Request password reset email

#### Request Body:
```json
{
  "email": "user@example.com"
}
```

#### Required Fields:
- `email` (string) - User's email address

#### Success Response (200):
```json
{
  "success": true,
  "message": "If the email exists in our system, you will receive a password reset link.",
  "data": null,
  "errors": null
}
```

**Note:** For security, this endpoint always returns success, regardless of whether the email exists.

---

### 9. **Reset Password**
**Endpoint:** `POST /api/auth/reset-password/`  
**Authentication:** Not required  
**Description:** Reset password using token from email

#### Request Body:
```json
{
  "token": "550e8400-e29b-41d4-a716-446655440000",
  "new_password": "NewSecurePass456!",
  "new_password_confirm": "NewSecurePass456!"
}
```

#### Required Fields:
- `token` (UUID string) - Password reset token from email
- `new_password` (string) - New password (minimum 8 characters)
- `new_password_confirm` (string) - Must match new_password

#### Success Response (200):
```json
{
  "success": true,
  "message": "Password reset successful",
  "data": null,
  "errors": null
}
```

---

## 👤 User Profile Endpoints

### 10. **Get User Profile**
**Endpoint:** `GET /api/auth/profile/`  
**Authentication:** Required (Bearer Token)  
**Description:** Get current user's profile information

#### Headers:
```
Authorization: Bearer <access_token>
```

#### Request Body:
None (GET request)

#### Success Response (200):
```json
{
  "success": true,
  "message": "Profile retrieved successfully",
  "data": {
    "id": 1,
    "email": "user@example.com",
    "username": "testuser",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "phone_number": "+1234567890",
    "date_of_birth": "1990-01-01",
    "profile_picture": null,
    "role": "customer",
    "is_email_verified": true,
    "is_phone_verified": false,
    "is_profile_complete": false,
    "address": "123 Main St",
    "city": "New York",
    "state": "NY",
    "country": "USA",
    "postal_code": "10001",
    "created_at": "2025-10-22T10:30:00Z",
    "last_login": "2025-10-22T15:45:00Z"
  },
  "errors": null
}
```

---

### 11. **Update User Profile**
**Endpoint:** `PUT /api/auth/profile/` or `PATCH /api/auth/profile/`  
**Authentication:** Required (Bearer Token)  
**Description:** Update user profile information

#### Headers:
```
Authorization: Bearer <access_token>
```

#### Request Body (PUT - Full Update):
```json
{
  "username": "newtestuser",
  "first_name": "Jane",
  "last_name": "Smith",
  "phone_number": "+1987654321",
  "date_of_birth": "1992-05-15",
  "address": "456 Oak Ave",
  "city": "Los Angeles",
  "state": "CA",
  "country": "USA",
  "postal_code": "90210"
}
```

#### Request Body (PATCH - Partial Update):
```json
{
  "first_name": "Jane",
  "phone_number": "+1987654321"
}
```

#### Editable Fields:
- `username` (string) - Must be unique, alphanumeric with underscores
- `first_name` (string) - User's first name
- `last_name` (string) - User's last name
- `phone_number` (string) - Valid phone format
- `date_of_birth` (date) - Format: YYYY-MM-DD
- `profile_picture` (file) - Image file
- `address` (string) - Street address
- `city` (string) - City name
- `state` (string) - State/Province
- `country` (string) - Country name
- `postal_code` (string) - ZIP/Postal code

#### Read-Only Fields:
- `id`, `email`, `role`, `is_email_verified`, `is_phone_verified`, `created_at`, `last_login`

#### Success Response (200):
```json
{
  "success": true,
  "message": "Profile updated successfully",
  "data": {
    "id": 1,
    "email": "user@example.com",
    "username": "newtestuser",
    "first_name": "Jane",
    "last_name": "Smith",
    "full_name": "Jane Smith",
    "phone_number": "+1987654321",
    "date_of_birth": "1992-05-15",
    "profile_picture": null,
    "role": "customer",
    "is_email_verified": true,
    "is_phone_verified": false,
    "is_profile_complete": true,
    "address": "456 Oak Ave",
    "city": "Los Angeles",
    "state": "CA",
    "country": "USA",
    "postal_code": "90210",
    "created_at": "2025-10-22T10:30:00Z",
    "last_login": "2025-10-22T15:45:00Z"
  },
  "errors": null
}
```

---

## 👥 Admin Endpoints

### 12. **List All Users** (Admin Only)
**Endpoint:** `GET /api/auth/users/`  
**Authentication:** Required (Bearer Token + Admin Role)  
**Description:** Get list of all users (admin/super_admin only)

#### Headers:
```
Authorization: Bearer <access_token>
```

#### Request Body:
None (GET request)

#### Query Parameters:
- `page` (integer) - Page number for pagination
- `page_size` (integer) - Number of results per page

#### Success Response (200):
```json
{
  "success": true,
  "message": "Users retrieved successfully",
  "data": [
    {
      "id": 1,
      "email": "user1@example.com",
      "username": "user1",
      "first_name": "John",
      "last_name": "Doe",
      "full_name": "John Doe",
      "role": "customer",
      "is_active": true,
      "is_email_verified": true,
      "created_at": "2025-10-22T10:30:00Z",
      "last_login": "2025-10-22T15:45:00Z"
    },
    {
      "id": 2,
      "email": "user2@example.com",
      "username": "user2",
      "first_name": "Jane",
      "last_name": "Smith",
      "full_name": "Jane Smith",
      "role": "barber",
      "is_active": true,
      "is_email_verified": true,
      "created_at": "2025-10-21T14:20:00Z",
      "last_login": "2025-10-22T12:30:00Z"
    }
  ],
  "errors": null
}
```

#### Error Response (403):
```json
{
  "success": false,
  "message": "Permission denied. Admin access required.",
  "data": null,
  "errors": null
}
```

---

## 🚀 Quick Test Examples

### cURL Commands:

#### 1. Register User:
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "first_name": "Test",
    "last_name": "User",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "role": "customer"
  }'
```

#### 2. Login User:
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

#### 3. Get Profile:
```bash
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 4. Update Profile:
```bash
curl -X PATCH http://localhost:8000/api/auth/profile/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "first_name": "Updated",
    "phone_number": "+1234567890"
  }'
```

---

## 🔒 Authentication

### JWT Token Usage:
1. **Login** to get access and refresh tokens
2. **Include access token** in Authorization header: `Bearer <access_token>`
3. **Refresh token** when access token expires using `/api/auth/token/refresh/`
4. **Logout** to blacklist refresh token

### Token Lifetimes:
- **Access Token:** 60 minutes
- **Refresh Token:** 7 days

---

## ⚠️ Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 201 | Created (Registration) |
| 400 | Bad Request (Validation errors) |
| 401 | Unauthorized (Invalid credentials/token) |
| 403 | Forbidden (Insufficient permissions) |
| 404 | Not Found |
| 500 | Internal Server Error |

---

## 📱 Frontend Integration

### JavaScript Example:
```javascript
// Login function
async function login(email, password) {
  const response = await fetch('http://localhost:8000/api/auth/login/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password })
  });
  
  const data = await response.json();
  
  if (data.success) {
    // Store tokens
    localStorage.setItem('access_token', data.data.access);
    localStorage.setItem('refresh_token', data.data.refresh);
    return data.data.user;
  } else {
    throw new Error(data.message);
  }
}

// API call with authentication
async function getProfile() {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch('http://localhost:8000/api/auth/profile/', {
    headers: {
      'Authorization': `Bearer ${token}`,
    }
  });
  
  const data = await response.json();
  return data;
}
```

---

## 🎯 User Roles & Permissions

| Role | Description | Can Access Admin Endpoints |
|------|-------------|----------------------------|
| `customer` | Regular customer | ❌ |
| `barber` | Barber/Stylist | ❌ |
| `barbershop` | Barbershop owner | ❌ |
| `admin` | Administrator | Limited ✅ |
| `super_admin` | Super administrator | Full ✅ |

---

## 🛡️ Super Admin API Endpoints

**Base URL:** `http://localhost:8000/api/super-admin/`

**Authentication:** Required - Bearer Token with `super_admin` role

---

### 📊 Dashboard Statistics

#### Get Dashboard Stats
**Endpoint:** `GET /api/super-admin/dashboard/stats/`  
**Authentication:** Super Admin required  
**Description:** Get comprehensive dashboard statistics

#### Success Response (200):
```json
{
  "success": true,
  "data": {
    "total_admins": 5,
    "total_barbershops": 25,
    "active_barbershops": 22,
    "total_revenue": "125000.00",
    "monthly_growth": 15.2
  },
  "message": "Dashboard statistics retrieved successfully"
}
```

#### Get Complete Dashboard Data
**Endpoint:** `GET /api/super-admin/dashboard/data/`  
**Authentication:** Super Admin required  
**Description:** Load all dashboard data including stats and recent users

#### Success Response (200):
```json
{
  "success": true,
  "data": {
    "stats": {
      "total_admins": 5,
      "total_barbershops": 25,
      "active_barbershops": 22,
      "total_revenue": "125000.00",
      "monthly_growth": 15.2
    },
    "recent_admins": [...],
    "recent_barbershops": [...]
  },
  "message": "Dashboard data loaded successfully"
}
```

---

### 👥 Admin Management

#### List All Admins
**Endpoint:** `GET /api/super-admin/admins/`  
**Authentication:** Super Admin required  
**Description:** Retrieve list of all admin users

#### Query Parameters:
- `search` (string) - Search by name or email
- `is_active` (boolean) - Filter by active status

#### Success Response (200):
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "email": "admin@example.com",
      "first_name": "John",
      "last_name": "Admin",
      "role": "admin",
      "is_active": true,
      "is_email_verified": true,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "managed_barbershops_count": 3,
      "created_by_name": "Super Admin"
    }
  ],
  "count": 1,
  "message": "Admins retrieved successfully"
}
```

#### Create New Admin
**Endpoint:** `POST /api/super-admin/admins/`  
**Authentication:** Super Admin required  
**Description:** Create a new admin user

#### Request Body:
```json
{
  "email": "newadmin@example.com",
  "first_name": "Jane",
  "last_name": "Admin",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!"
}
```

#### Success Response (201):
```json
{
  "success": true,
  "data": {
    "id": 2,
    "email": "newadmin@example.com",
    "first_name": "Jane",
    "last_name": "Admin",
    "role": "admin",
    "is_active": true,
    "created_at": "2024-01-15T11:00:00Z"
  },
  "message": "Admin created successfully"
}
```

#### Get Admin Details
**Endpoint:** `GET /api/super-admin/admins/{id}/`  
**Authentication:** Super Admin required  
**Description:** Retrieve detailed information about a specific admin

#### Update Admin
**Endpoint:** `PUT /api/super-admin/admins/{id}/`  
**Authentication:** Super Admin required  
**Description:** Update admin information

#### Request Body:
```json
{
  "first_name": "Updated Name",
  "last_name": "Updated Last",
  "is_active": false,
  "phone_number": "+1234567890"
}
```

#### Delete Admin
**Endpoint:** `DELETE /api/super-admin/admins/{id}/`  
**Authentication:** Super Admin required  
**Description:** Delete an admin (only if they haven't created any barbershops)

#### Toggle Admin Status
**Endpoint:** `PATCH /api/super-admin/admins/{id}/toggle-status/`  
**Authentication:** Super Admin required  
**Description:** Activate/deactivate an admin

---

### ✂️ Barbershop Management

#### List All Barbershops
**Endpoint:** `GET /api/super-admin/barbershops/`  
**Authentication:** Super Admin required  
**Description:** Retrieve list of all barbershop users

#### Query Parameters:
- `search` (string) - Search by shop name, owner name, or email
- `is_active` (boolean) - Filter by active status
- `plan` (string) - Filter by subscription plan

#### Success Response (200):
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "email": "shop@example.com",
      "name": "Mike Wilson",
      "shop_name": "Cut & Style Barbershop",
      "shop_owner_name": "Mike Wilson",
      "shop_logo": "/media/shop_logos/logo.jpg",
      "address": "123 Main St, New York, NY",
      "phone_number": "+1-555-0123",
      "role": "barbershop",
      "is_active": true,
      "is_email_verified": true,
      "created_at": "2024-03-01T09:00:00Z",
      "updated_at": "2024-03-01T09:00:00Z",
      "subscription": {
        "id": 1,
        "plan": "premium",
        "status": "active",
        "expires_at": "2025-03-01T09:00:00Z",
        "is_active": true,
        "days_remaining": 365
      },
      "created_by_name": "John Admin"
    }
  ],
  "count": 1,
  "message": "Barbershops retrieved successfully"
}
```

#### Create New Barbershop
**Endpoint:** `POST /api/super-admin/barbershops/`  
**Authentication:** Super Admin required  
**Description:** Create a new barbershop user with subscription

#### Request Body:
```json
{
  "email": "newshop@example.com",
  "shop_name": "New Barbershop",
  "shop_owner_name": "Owner Name",
  "address": "456 Oak Ave, Los Angeles, CA",
  "phone_number": "+1-555-0456",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "subscription_plan": "basic"
}
```

#### Success Response (201):
```json
{
  "success": true,
  "data": {
    "id": 2,
    "email": "newshop@example.com",
    "shop_name": "New Barbershop",
    "shop_owner_name": "Owner Name",
    "subscription": {
      "plan": "basic",
      "status": "active",
      "expires_at": "2025-01-15T12:00:00Z"
    }
  },
  "message": "Barbershop created successfully"
}
```

#### Get Barbershop Details
**Endpoint:** `GET /api/super-admin/barbershops/{id}/`  
**Authentication:** Super Admin required  
**Description:** Retrieve detailed information about a specific barbershop

#### Update Barbershop
**Endpoint:** `PUT /api/super-admin/barbershops/{id}/`  
**Authentication:** Super Admin required  
**Description:** Update barbershop information and subscription

#### Request Body:
```json
{
  "shop_name": "Updated Shop Name",
  "shop_owner_name": "Updated Owner",
  "address": "New Address",
  "phone_number": "+1-555-9999",
  "is_active": true,
  "subscription_plan": "premium",
  "subscription_status": "active"
}
```

#### Delete Barbershop
**Endpoint:** `DELETE /api/super-admin/barbershops/{id}/`  
**Authentication:** Super Admin required  
**Description:** Delete a barbershop (only if no active subscription)

#### Toggle Barbershop Status
**Endpoint:** `PATCH /api/super-admin/barbershops/{id}/toggle-status/`  
**Authentication:** Super Admin required  
**Description:** Activate/deactivate a barbershop

---

## 🔒 Authentication Examples

### cURL Examples:

#### Get Dashboard Stats:
```bash
curl -X GET "http://localhost:8000/api/super-admin/dashboard/stats/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

#### Create Admin:
```bash
curl -X POST "http://localhost:8000/api/super-admin/admins/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newadmin@example.com",
    "first_name": "Jane",
    "last_name": "Admin",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!"
  }'
```

#### Create Barbershop:
```bash
curl -X POST "http://localhost:8000/api/super-admin/barbershops/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newshop@example.com",
    "shop_name": "New Barbershop",
    "shop_owner_name": "Owner Name",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "subscription_plan": "basic"
  }'
```

---

## 🎯 Updated User Roles & Permissions

| Role | Description | Can Access Super Admin APIs |
|------|-------------|----------------------------|
| `customer` | Regular customer | ❌ |
| `barber` | Barber/Stylist | ❌ |
| `barbershop` | Barbershop owner | ❌ |
| `admin` | Administrator | ❌ |
| `super_admin` | Super administrator | ✅ |

---

This documentation covers all authentication and super admin endpoints with complete request/response examples. Save this as your API reference guide!