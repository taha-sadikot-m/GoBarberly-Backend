# Barbershop Operations API Documentation

## Overview
The Barbershop Operations API provides comprehensive endpoints for barbershop business management, including appointments, sales, staff management, customer management, inventory tracking, and business analytics.

## Base URL
```
/api/barbershop/
```

## Authentication
All endpoints require authentication with a valid JWT token and the user must have the `barbershop` role.

## API Endpoints

### Dashboard Endpoints

#### Get Dashboard Statistics
**GET** `/dashboard/stats/`

Returns comprehensive dashboard statistics for the barbershop.

**Response:**
```json
{
  "today_appointments": 8,
  "pending_appointments": 3,
  "completed_appointments": 5,
  "cancelled_appointments": 0,
  "today_sales": "750.00",
  "total_sales": "15420.50",
  "active_staff": 4,
  "total_customers": 156,
  "low_stock_items": 2
}
```

#### Get Monthly Revenue Data
**GET** `/dashboard/monthly-revenue/`

Returns monthly revenue data for the last 12 months.

**Response:**
```json
[
  {
    "month": "January 2024",
    "revenue": "8420.50",
    "appointments": 145
  },
  ...
]
```

#### Get Service Popularity
**GET** `/dashboard/service-popularity/`

Returns service popularity statistics.

**Response:**
```json
[
  {
    "service": "Haircut",
    "count": 89,
    "revenue": "2225.00"
  },
  ...
]
```

#### Get Staff Performance
**GET** `/dashboard/staff-performance/`

Returns staff performance data.

**Response:**
```json
[
  {
    "barber_name": "John Smith",
    "staff_name": "John Smith",
    "total_services": 45,
    "total_revenue": "1125.00"
  },
  ...
]
```

### Appointment Endpoints

#### List/Create Appointments
**GET/POST** `/appointments/`

**Query Parameters (GET):**
- `date` - Filter by specific date (YYYY-MM-DD)
- `status` - Filter by status (pending, confirmed, completed, cancelled, no_show)
- `barber` - Filter by barber name

**POST Body:**
```json
{
  "customer_name": "John Doe",
  "customer_phone": "+1234567890",
  "service": "Haircut",
  "appointment_date": "2024-01-15",
  "appointment_time": "14:30",
  "barber_name": "Jane Smith",
  "duration_minutes": 30,
  "notes": "Customer prefers short sides"
}
```

#### Get/Update/Delete Appointment
**GET/PUT/PATCH/DELETE** `/appointments/{id}/`

#### Get Today's Appointments
**GET** `/appointments/today/`

Returns all appointments scheduled for today.

#### Update Appointment Status
**PATCH** `/appointments/{id}/status/`

**Body:**
```json
{
  "status": "completed"
}
```

### Sales Endpoints

#### List/Create Sales
**GET/POST** `/sales/`

**Query Parameters (GET):**
- `start_date` - Start date for filtering (YYYY-MM-DD)
- `end_date` - End date for filtering (YYYY-MM-DD)
- `payment_method` - Filter by payment method
- `service` - Filter by service type

**POST Body:**
```json
{
  "customer_name": "John Doe",
  "service": "Haircut",
  "amount": "25.00",
  "payment_method": "Cash",
  "sale_date": "2024-01-15",
  "barber_name": "Jane Smith"
}
```

#### Get/Update/Delete Sale
**GET/PUT/PATCH/DELETE** `/sales/{id}/`

#### Get Daily Sales Summary
**GET** `/sales/daily-summary/`

**Query Parameters:**
- `date` - Specific date (defaults to today)

**Response:**
```json
{
  "total_sales": "750.00",
  "total_transactions": 12,
  "payment_breakdown": [
    {
      "payment_method": "Cash",
      "count": 8,
      "amount": "520.00"
    },
    {
      "payment_method": "Card",
      "count": 4,
      "amount": "230.00"
    }
  ],
  "service_breakdown": [
    {
      "service": "Haircut",
      "count": 10,
      "amount": "650.00"
    },
    {
      "service": "Beard Trim",
      "count": 2,
      "amount": "100.00"
    }
  ]
}
```

### Staff Endpoints

#### List/Create Staff
**GET/POST** `/staff/`

**Query Parameters (GET):**
- `status` - Filter by status (Active, Inactive, On Leave)
- `role` - Filter by role (Barber, Senior Barber, Stylist, etc.)

**POST Body:**
```json
{
  "name": "John Smith",
  "role": "Barber",
  "phone": "+1234567890",
  "email": "john@barbershop.com",
  "hire_date": "2024-01-01",
  "salary": "3000.00",
  "status": "Active",
  "skills": ["Haircut", "Beard Trim"],
  "commission_rate": "15.00"
}
```

#### Get/Update/Delete Staff
**GET/PUT/PATCH/DELETE** `/staff/{id}/`

#### Get Active Barbers
**GET** `/staff/active-barbers/`

Returns list of active barbers for appointment booking.

#### Staff Availability
**GET/POST** `/staff/availability/`

Manage staff availability schedules.

### Customer Endpoints

#### List/Create Customers
**GET/POST** `/customers/`

**Query Parameters (GET):**
- `search` - Search by name or phone number

**POST Body:**
```json
{
  "name": "John Doe",
  "phone": "+1234567890",
  "email": "john@example.com",
  "date_of_birth": "1990-01-01",
  "preferences": "Prefers short haircuts",
  "notes": "Regular customer"
}
```

#### Get/Update/Delete Customer
**GET/PUT/PATCH/DELETE** `/customers/{id}/`

#### Update Customer Statistics
**POST** `/customers/{id}/update-stats/`

Updates customer visit statistics based on their appointment and sales history.

### Inventory Endpoints

#### List/Create Inventory Items
**GET/POST** `/inventory/`

**Query Parameters (GET):**
- `category` - Filter by category
- `stock_status` - Filter by stock status (low_stock, out_of_stock)

**POST Body:**
```json
{
  "name": "Hair Gel",
  "category": "Hair Products",
  "quantity": 50,
  "unit": "bottle",
  "cost_per_unit": "5.00",
  "selling_price": "8.00",
  "min_stock": 10,
  "supplier": "Beauty Supply Co",
  "supplier_contact": "+1234567890"
}
```

#### Get/Update/Delete Inventory Item
**GET/PUT/PATCH/DELETE** `/inventory/{id}/`

#### Get Low Stock Alerts
**GET** `/inventory/low-stock/`

Returns items that are at or below minimum stock level.

### Activity Log Endpoints

#### List Activity Logs
**GET** `/activity-logs/`

**Query Parameters:**
- `action_type` - Filter by action type
- `start_date` - Start date for filtering

Returns the last 100 activity log entries.

### Reports Endpoints

#### Get Reports Summary
**GET** `/reports/summary/`

**Query Parameters:**
- `start_date` - Start date for reporting period
- `end_date` - End date for reporting period

**Response:**
```json
{
  "date_range": {
    "start": "2024-01-01",
    "end": "2024-01-31"
  },
  "revenue": {
    "total_revenue": "15420.50",
    "total_transactions": 156,
    "avg_transaction": "98.85"
  },
  "appointments": {
    "total_appointments": 168,
    "completed_appointments": 156,
    "cancelled_appointments": 12
  },
  "services": [...],
  "staff_performance": [...]
}
```

#### Get Business Analytics
**GET** `/reports/analytics/`

Returns comprehensive business analytics including daily revenue trends, service performance, customer retention metrics, and peak hours analysis.

#### Export Data
**GET** `/reports/export/`

**Query Parameters:**
- `type` - Data type to export (all, appointments, sales, customers, inventory)
- `start_date` - Start date for export
- `end_date` - End date for export

### Calendar and Scheduling Endpoints

#### Get Calendar View
**GET** `/calendar/`

**Query Parameters:**
- `month` - Month number (1-12)
- `year` - Year (YYYY)

Returns calendar view with appointments grouped by date.

#### Get Schedule Grid
**GET** `/schedule/grid/`

**Query Parameters:**
- `date` - Specific date (YYYY-MM-DD)

Returns detailed schedule grid for a specific date with time slots and staff.

#### Get Available Time Slots
**GET** `/schedule/available-slots/`

**Query Parameters:**
- `date` - Date to check (YYYY-MM-DD) - Required
- `barber` - Barber name (optional)

Returns available time slots for booking.

#### Block Time Slot
**POST** `/schedule/block-slot/`

**Body:**
```json
{
  "date": "2024-01-15",
  "time": "15:00",
  "barber_name": "John Smith",
  "reason": "Lunch Break"
}
```

### Quick Actions Endpoints

#### Create Quick Appointment
**POST** `/quick/appointment/`

Create a walk-in appointment for immediate service.

**Body:**
```json
{
  "customer_name": "Walk-in Customer",
  "customer_phone": "+1234567890",
  "service": "Quick Trim",
  "barber_name": "John Smith"
}
```

#### Create Quick Sale
**POST** `/quick/sale/`

Record a quick sale transaction.

**Body:**
```json
{
  "customer_name": "Walk-in Customer",
  "service": "Haircut",
  "amount": "25.00",
  "payment_method": "Cash",
  "barber_name": "John Smith"
}
```

## Error Responses

All endpoints return appropriate HTTP status codes and error messages:

```json
{
  "error": "Error message description",
  "details": "Additional error details if applicable"
}
```

## Permissions

- All endpoints require the user to be authenticated
- Users can only access their own barbershop data (data isolation)
- The `IsBarbershop` permission class ensures only barbershop role users can access these endpoints
- The `CanAccessOwnData` permission class ensures users can only access their own records

## Rate Limiting

API endpoints are subject to rate limiting to prevent abuse. The current limits are:
- 1000 requests per hour for authenticated users
- 100 requests per hour for unauthenticated requests

## Data Models

### Key Models Structure

1. **BarbershopAppointment** - Appointment scheduling and management
2. **BarbershopSale** - Sales transactions and revenue tracking
3. **BarbershopStaff** - Staff management and performance
4. **BarbershopCustomer** - Customer relationship management
5. **BarbershopInventory** - Inventory tracking and alerts
6. **BarbershopActivityLog** - Activity logging and audit trail
7. **BarbershopStaffAvailability** - Staff scheduling and availability

## Usage Examples

### Creating an Appointment
```javascript
const response = await fetch('/api/barbershop/appointments/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    customer_name: 'John Doe',
    customer_phone: '+1234567890',
    service: 'Haircut',
    appointment_date: '2024-01-15',
    appointment_time: '14:30',
    barber_name: 'Jane Smith',
    duration_minutes: 30
  })
});
```

### Getting Dashboard Stats
```javascript
const response = await fetch('/api/barbershop/dashboard/stats/', {
  headers: {
    'Authorization': 'Bearer ' + token
  }
});
const stats = await response.json();
```

### Filtering Appointments
```javascript
const response = await fetch('/api/barbershop/appointments/?date=2024-01-15&status=confirmed', {
  headers: {
    'Authorization': 'Bearer ' + token
  }
});
```

This API provides comprehensive functionality for managing all aspects of a barbershop business, from scheduling and sales to inventory and analytics.