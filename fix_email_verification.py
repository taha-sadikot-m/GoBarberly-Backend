#!/usr/bin/env python
"""
Fix email verification for existing users
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def fix_email_verification():
    """Fix email verification for all users"""
    print("Fixing email verification for all users...")
    
    users = User.objects.all()
    updated_count = 0
    
    for user in users:
        if not user.is_email_verified:
            user.is_email_verified = True
            user.save(update_fields=['is_email_verified'])
            updated_count += 1
            print(f"✅ Fixed email verification for: {user.email} ({user.role})")
        else:
            print(f"ℹ️  Email already verified for: {user.email} ({user.role})")
    
    print(f"\n🎉 Fixed email verification for {updated_count} users")
    print(f"📊 Total users: {users.count()}")

if __name__ == '__main__':
    fix_email_verification()