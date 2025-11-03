#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from barbershop_operations.models import BarbershopInventory, User

print("=== INVENTORY DEBUG INFO ===")

# Check if there are any barbershop users
barbershop_users = User.objects.filter(role='barbershop')
print(f"\nBarbershop users: {barbershop_users.count()}")
for user in barbershop_users:
    print(f"  - {user.email} (ID: {user.id})")

# Check inventory items
inventory_items = BarbershopInventory.objects.all()
print(f"\nTotal inventory items: {inventory_items.count()}")

for item in inventory_items:
    print(f"\nInventory Item ID: {item.id}")
    print(f"  Name: {item.name}")
    print(f"  Category: {item.category}")
    print(f"  Quantity: {item.quantity}")
    print(f"  Min Stock: {item.min_stock}")
    print(f"  Unit Cost: {item.unit_cost}")
    print(f"  Supplier: '{item.supplier}' (type: {type(item.supplier)})")
    print(f"  Barbershop: {item.barbershop.email if item.barbershop else 'None'}")
    print(f"  Created: {item.created_at}")

# Create a test item if none exist and we have a barbershop user
if inventory_items.count() == 0 and barbershop_users.count() > 0:
    print("\n=== CREATING TEST INVENTORY ITEM ===")
    barbershop = barbershop_users.first()
    test_item = BarbershopInventory.objects.create(
        barbershop=barbershop,
        name="Test Hair Gel",
        category="Hair Products",
        quantity=50,
        min_stock=10,
        unit_cost=25.50,
        supplier="ABC Beauty Supplies"
    )
    print(f"Created test item: {test_item.name} with supplier: '{test_item.supplier}'")

print("\n=== END DEBUG ===")