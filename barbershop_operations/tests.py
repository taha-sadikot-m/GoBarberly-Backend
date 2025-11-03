"""
Tests for Barbershop Operations API endpoints
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date, time
from barbershop_operations.models import (
    BarbershopAppointment, BarbershopSale, BarbershopStaff, 
    BarbershopCustomer, BarbershopInventory, BarbershopActivityLog
)

User = get_user_model()


class BarbershopOperationsAPITestCase(TestCase):
    """Base test case for barbershop operations"""
    
    def setUp(self):
        """Set up test data"""
        # Create barbershop user
        self.barbershop_user = User.objects.create_user(
            username='testbarbershop',
            email='test@barbershop.com',
            password='testpass123',
            role='barbershop',
            shop_name='Test Barbershop',
            phone_number='+1234567890',
            address='123 Test Street'
        )
        
        # Create API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.barbershop_user)
        
        # Create test data
        self.create_test_data()
    
    def create_test_data(self):
        """Create test data for barbershop"""
        # Create staff
        self.staff = BarbershopStaff.objects.create(
            barbershop=self.barbershop_user,
            name='John Barber',
            role='Barber',
            phone='+1234567891',
            email='john@barbershop.com',
            hire_date=date.today(),
            salary=Decimal('3000.00'),
            status='Active'
        )
        
        # Create customer
        self.customer = BarbershopCustomer.objects.create(
            barbershop=self.barbershop_user,
            name='Test Customer',
            phone='+1234567892',
            email='customer@test.com'
        )
        
        # Create appointment
        self.appointment = BarbershopAppointment.objects.create(
            barbershop=self.barbershop_user,
            customer_name='Test Customer',
            customer_phone='+1234567892',
            service='Haircut',
            appointment_date=date.today(),
            appointment_time=time(10, 0),
            barber_name='John Barber',
            status='confirmed',
            duration_minutes=30
        )
        
        # Create sale
        self.sale = BarbershopSale.objects.create(
            barbershop=self.barbershop_user,
            customer_name='Test Customer',
            service='Haircut',
            amount=Decimal('25.00'),
            payment_method='Cash',
            sale_date=date.today(),
            barber_name='John Barber'
        )
        
        # Create inventory item
        self.inventory = BarbershopInventory.objects.create(
            barbershop=self.barbershop_user,
            name='Hair Gel',
            category='Hair Products',
            quantity=50,
            unit='bottle',
            cost_per_unit=Decimal('5.00'),
            selling_price=Decimal('8.00'),
            min_stock=10,
            supplier='Beauty Supply Co'
        )


class DashboardAPITests(BarbershopOperationsAPITestCase):
    """Test dashboard API endpoints"""
    
    def test_dashboard_stats(self):
        """Test dashboard statistics endpoint"""
        url = reverse('barbershop_operations:dashboard_stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('today_appointments', response.data)
        self.assertIn('total_sales', response.data)
        self.assertIn('active_staff', response.data)
    
    def test_monthly_revenue(self):
        """Test monthly revenue endpoint"""
        url = reverse('barbershop_operations:monthly_revenue')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_service_popularity(self):
        """Test service popularity endpoint"""
        url = reverse('barbershop_operations:service_popularity')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)


class AppointmentAPITests(BarbershopOperationsAPITestCase):
    """Test appointment API endpoints"""
    
    def test_list_appointments(self):
        """Test listing appointments"""
        url = reverse('barbershop_operations:appointment_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_create_appointment(self):
        """Test creating new appointment"""
        url = reverse('barbershop_operations:appointment_list_create')
        data = {
            'customer_name': 'New Customer',
            'customer_phone': '+1234567893',
            'service': 'Beard Trim',
            'appointment_date': date.today(),
            'appointment_time': time(14, 0),
            'barber_name': 'John Barber',
            'duration_minutes': 30
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['customer_name'], 'New Customer')
    
    def test_update_appointment_status(self):
        """Test updating appointment status"""
        url = reverse('barbershop_operations:update_appointment_status', 
                     kwargs={'appointment_id': self.appointment.id})
        data = {'status': 'completed'}
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')
    
    def test_today_appointments(self):
        """Test getting today's appointments"""
        url = reverse('barbershop_operations:today_appointments')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)


# Additional test classes would continue here...
# For brevity, showing the structure with key test cases
