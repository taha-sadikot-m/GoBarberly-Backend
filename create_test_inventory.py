#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from barbershop_operations.models import BarbershopInventory, User

# Get the first barbershop user (likely the one used in frontend)
barbershop_users = User.objects.filter(role='barbershop').order_by('id')
if barbershop_users.exists():
    first_user = barbershop_users.first()
    print(f"Creating inventory item for: {first_user.email}")
    
    # Create an inventory item with supplier data
    item = BarbershopInventory.objects.create(
        barbershop=first_user,
        name="Premium Hair Shampoo",
        category="Hair Products",
        quantity=25,
        min_stock=5,
        unit_cost=45.75,
        supplier="Premium Beauty Supplies Ltd."
    )
    
    print(f"Created inventory item:")
    print(f"  ID: {item.id}")
    print(f"  Name: {item.name}")
    print(f"  Supplier: '{item.supplier}'")
    print(f"  Unit Cost: {item.unit_cost}")
    print(f"  For User: {item.barbershop.email}")
else:
    print("No barbershop users found!")

# Also create one for the user who has the existing item
existing_user = User.objects.get(email='524410034@nitkkr.ac.in')
item2 = BarbershopInventory.objects.create(
    barbershop=existing_user,
    name="Hair Conditioner",
    category="Hair Products", 
    quantity=30,
    min_stock=8,
    unit_cost=35.25,
    supplier="Beauty World Inc."
)

print(f"\nCreated second inventory item:")
print(f"  ID: {item2.id}")
print(f"  Name: {item2.name}")
print(f"  Supplier: '{item2.supplier}'")
print(f"  Unit Cost: {item2.unit_cost}")
print(f"  For User: {item2.barbershop.email}")