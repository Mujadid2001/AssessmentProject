#!/usr/bin/env python
"""
Initialize ELD system - Run migrations and create sample data
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(__file__))

django.setup()

from django.core.management import call_command
from api.models import Driver

def init_database():
    """Initialize database with migrations"""
    print("Running migrations...")
    call_command('migrate')
    print("✓ Migrations complete")

def create_sample_driver():
    """Create sample driver for testing"""
    driver, created = Driver.objects.get_or_create(
        license_number="DL-TEST001",
        defaults={
            "first_name": "John",
            "last_name": "Peterbilt",
            "current_location": "Chicago, IL",
            "cycle_hours_used": 32.5,
        }
    )
    
    if created:
        print(f"✓ Created sample driver: {driver.first_name} {driver.last_name}")
    else:
        print(f"✓ Sample driver already exists")
    
    return driver

if __name__ == "__main__":
    print("=== ELD System Initialization ===\n")
    
    try:
        init_database()
        driver = create_sample_driver()
        
        print("\n✓ Initialization complete!")
        print(f"\nSample Driver ID: {driver.id}")
        print(f"License: {driver.license_number}")
        print("\nNext steps:")
        print("1. Run: python manage.py runserver")
        print("2. Backend API: http://localhost:8000/api")
        print("3. Frontend: npm run dev (from frontend/)")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
