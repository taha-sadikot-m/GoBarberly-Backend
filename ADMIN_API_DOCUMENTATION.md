# Admin Dashboard Backend API Documentation

## Overview

This document describes the complete backend API implementation for the Admin Dashboard functionality. The admin user can manage barbershops they have created, view scoped statistics, track activities, and manage appointments.

## Authentication & Authorization

### Admin Role Access
- **Role Required**: `admin`
- **Scope**: Admin users can only access barbershops they created (`created_by` relationship)
- **Authentication**: JWT Bearer Token required for all endpoints

### Permission Classes
- `IsAdmin`: Verifies user has 'admin' role
- `CanManageOwnBarbershops`: Ensures admin can only manage barbershops they created
- `CanViewOwnData`: Allows viewing data only for admin-created barbershops

## API Endpoints

### Dashboard Statistics

#### Get Dashboard Stats
```
GET /api/admin/dashboard/stats/
```
**Description**: Get key statistics for admin's barbershops

**Response Example**:
```json
{
  "total_barbershops": 4,
  "active_barbershops": 4,
  "total_appointments": 60,
  "monthly_revenue": "967.00"
}
```

#### Get Complete Dashboard Data
```
GET /api/admin/dashboard/data/
```
**Description**: Get comprehensive dashboard data including stats, recent activities, appointments, and barbershop summary

**Response Example**:
```json
{
  "stats": {
    "total_barbershops": 4,
    "active_barbershops": 4,
    "total_appointments": 60,
    "monthly_revenue": "967.00"
  },
  "recent_activities": [...],
  "recent_appointments": [...],
  "barbershop_summary": [...]
}
```

### Barbershop Management

#### List Barbershops
```
GET /api/admin/barbershops/
```
**Description**: Get paginated list of barbershops created by admin

**Query Parameters**:
- `search`: Search by shop name, owner name, or email
- `status`: Filter by 'active' or 'inactive'
- `plan`: Filter by subscription plan ('basic', 'premium', 'enterprise')
- `page`: Page number for pagination
- `page_size`: Items per page (max 100)

**Response Example**:
```json
{
  "count": 4,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 10,
      "email": "barbershop4@test.com",
      "name": "Owner 4",
      "shop_name": "Test Barbershop 4",
      "shop_owner_name": "Owner 4",
      "shop_logo": null,
      "address": "130 Main St, Test City",
      "phone_number": "+12345678903",
      "role": "barbershop",
      "is_active": true,
      "is_email_verified": true,
      "created_at": "2025-01-24T18:01:49.228125Z",
      "updated_at": "2025-01-24T18:01:49.228150Z",
      "subscription": {
        "plan": "premium",
        "status": "active",
        "expires_at": "2025-02-23T18:01:49.338000Z",
        "is_active": true,
        "days_remaining": 30
      },
      "total_appointments": 15,
      "monthly_revenue": "207.00",
      "last_activity": {
        "action_type": "settings_changed",
        "description": "Account settings modified",
        "timestamp": "2025-01-23T19:01:49.571000Z"
      }
    }
  ]
}
```

#### Create Barbershop
```
POST /api/admin/barbershops/
```
**Description**: Create a new barbershop user

**Request Body**:
```json
{
  "email": "newshop@example.com",
  "shop_name": "New Barbershop",
  "shop_owner_name": "Owner Name",
  "address": "123 Main St, City",
  "phone_number": "+1234567890",
  "password": "SecurePass123",
  "password_confirm": "SecurePass123",
  "subscription_plan": "premium"
}
```

#### Get/Update/Delete Barbershop
```
GET /api/admin/barbershops/{id}/
PUT /api/admin/barbershops/{id}/
PATCH /api/admin/barbershops/{id}/
DELETE /api/admin/barbershops/{id}/
```
**Description**: Manage individual barbershop

**Update Request Body**:
```json
{
  "shop_name": "Updated Shop Name",
  "shop_owner_name": "Updated Owner",
  "address": "New Address",
  "phone_number": "+1234567890",
  "is_active": true,
  "subscription_plan": "enterprise",
  "subscription_status": "active"
}
```

#### Toggle Barbershop Status
```
POST /api/admin/barbershops/{id}/toggle-status/
```
**Description**: Toggle barbershop active/inactive status

**Response**:
```json
{
  "message": "Barbershop activated successfully.",
  "is_active": true
}
```

#### Get Barbershop Analytics
```
GET /api/admin/barbershops/{id}/analytics/
```
**Description**: Get detailed analytics for a specific barbershop

**Query Parameters**:
- `days`: Number of days to analyze (default: 30)

**Response Example**:
```json
{
  "barbershop": {...},
  "period_days": 30,
  "total_appointments": 15,
  "completed_appointments": 8,
  "completion_rate": 53.3,
  "total_revenue": "207.00",
  "average_revenue_per_appointment": "25.88",
  "monthly_breakdown": [
    {
      "month": "2025-01",
      "appointments": 15,
      "revenue": "207.00"
    }
  ],
  "recent_activities": [...]
}
```

### Activity Management

#### List Activities
```
GET /api/admin/activities/
```
**Description**: Get paginated activity feed for admin's barbershops

**Query Parameters**:
- `action_type`: Filter by activity type
- `barbershop`: Filter by barbershop ID
- `start_date`: Filter by start date (YYYY-MM-DD)
- `end_date`: Filter by end date (YYYY-MM-DD)
- `page`: Page number
- `page_size`: Items per page (max 200)

**Response Example**:
```json
{
  "count": 124,
  "next": "...",
  "previous": null,
  "results": [
    {
      "id": 144,
      "barbershop": 10,
      "barbershop_name": "Test Barbershop 4",
      "barbershop_owner": "Owner 4",
      "action_type": "login",
      "description": "User logged in to system",
      "amount": null,
      "timestamp": "2025-01-23T19:01:49.571000Z",
      "time_ago": "19 hours ago",
      "metadata": {
        "auto_generated": true,
        "test_data": true
      }
    }
  ]
}
```

### Appointment Management

#### List/Create Appointments
```
GET /api/admin/appointments/
POST /api/admin/appointments/
```
**Description**: Manage appointments for admin's barbershops

**Query Parameters** (GET):
- `status`: Filter by appointment status
- `barbershop`: Filter by barbershop ID
- `start_date`: Filter by start date
- `end_date`: Filter by end date
- `page`: Page number
- `page_size`: Items per page

**Create Request Body** (POST):
```json
{
  "barbershop": 7,
  "customer_name": "John Doe",
  "customer_email": "john@example.com",
  "customer_phone": "+1234567890",
  "service": "Haircut",
  "amount": "35.00",
  "appointment_date": "2025-01-25T10:00:00Z",
  "duration": 60,
  "notes": "Regular customer"
}
```

#### Get/Update/Delete Appointment
```
GET /api/admin/appointments/{id}/
PUT /api/admin/appointments/{id}/
PATCH /api/admin/appointments/{id}/
DELETE /api/admin/appointments/{id}/
```

## Data Models

### Activity Model
```python
{
  "barbershop": ForeignKey(User),
  "action_type": CharField(choices=[
    'appointment_created', 'appointment_updated', 'appointment_cancelled',
    'appointment_completed', 'payment_received', 'profile_updated',
    'subscription_updated', 'login', 'settings_changed'
  ]),
  "description": TextField,
  "amount": DecimalField(optional),
  "timestamp": DateTimeField,
  "metadata": JSONField
}
```

### Appointment Model
```python
{
  "barbershop": ForeignKey(User),
  "customer_name": CharField,
  "customer_email": EmailField,
  "customer_phone": CharField,
  "service": CharField,
  "amount": DecimalField,
  "appointment_date": DateTimeField,
  "duration": IntegerField,
  "status": CharField(choices=[
    'scheduled', 'confirmed', 'in_progress', 
    'completed', 'cancelled', 'no_show'
  ]),
  "notes": TextField,
  "created_at": DateTimeField,
  "updated_at": DateTimeField
}
```

## Error Handling

### Common HTTP Status Codes
- `200`: Success
- `201`: Created
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (invalid/missing token)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found (resource doesn't exist or access denied)
- `500`: Internal Server Error

### Error Response Format
```json
{
  "error": "Error message description"
}
```

## Security Features

### Scope Restrictions
- All endpoints filter data by `created_by` relationship
- Admin users can only see barbershops they created
- Activity logs track all admin actions
- Automatic logging of profile updates and status changes

### Data Validation
- Email uniqueness validation
- Password strength requirements
- Phone number format validation
- Appointment date validation (future dates only)
- Subscription plan validation

## Test Data

The system includes a management command to create test data:

```bash
python manage.py create_admin_test_data \
  --admin-email admin@gobarberly.com \
  --admin-password AdminPass123 \
  --barbershops 4 \
  --appointments 15
```

## API Testing Results

✅ **All endpoints tested and working**:
- Admin authentication: ✅
- Dashboard statistics: ✅ (4 barbershops, 60 appointments, $967 monthly revenue)
- Barbershop management: ✅ (CRUD operations with scope)
- Activity tracking: ✅ (124 activities logged)
- Appointment management: ✅ (60 appointments across barbershops)
- Filtering and pagination: ✅
- Analytics and reporting: ✅

## Frontend Integration

The admin API is designed to work seamlessly with the `AdminDashboard.tsx` component:

### Key Features Supported
1. **Dashboard Overview**: Real-time statistics and charts
2. **Barbershop Management**: Create, update, activate/deactivate shops
3. **Activity Feed**: Real-time activity tracking with filters
4. **Appointment Management**: Schedule and manage appointments
5. **Analytics**: Detailed performance metrics per barbershop
6. **Search & Filtering**: Advanced query capabilities

### Authentication Flow
1. Login with admin credentials
2. Receive JWT tokens and user info
3. Use Bearer token for all subsequent requests
4. Automatic scope filtering ensures data security

The implementation is complete and ready for production use with proper scope restrictions, comprehensive logging, and robust error handling.