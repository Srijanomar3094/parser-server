#!/usr/bin/env python3
"""
Test script to verify MongoDB connection and basic operations.
Run this script to ensure MongoDB is properly configured.
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Set Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parser.settings')
django.setup()

from django.db import connection
from contracts.models import Contract


def test_mongodb_connection():
    """Test MongoDB connection and basic operations."""
    try:
        # Test database connection
        connection.ensure_connection()
        print("✅ MongoDB connection successful!")
        
        # Test creating a contract
        contract = Contract.objects.create(
            original_filename="test_connection.pdf",
            status=Contract.STATUS_PENDING
        )
        print(f"✅ Contract created successfully with ID: {contract.id}")
        
        # Test retrieving the contract
        retrieved_contract = Contract.objects.get(pk=contract.id)
        print(f"✅ Contract retrieved successfully: {retrieved_contract.original_filename}")
        
        # Test updating the contract
        retrieved_contract.status = Contract.STATUS_COMPLETED
        retrieved_contract.save()
        print("✅ Contract updated successfully")
        
        # Test deleting the contract
        retrieved_contract.delete()
        print("✅ Contract deleted successfully")
        
        print("\n🎉 All MongoDB tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ MongoDB test failed: {e}")
        return False


def test_database_info():
    """Display database information."""
    try:
        # Get database info
        db_name = connection.settings_dict['NAME']
        db_engine = connection.settings_dict['ENGINE']
        db_host = connection.settings_dict['CLIENT']['host']
        db_port = connection.settings_dict['CLIENT']['port']
        
        print(f"\n📊 Database Information:")
        print(f"   Engine: {db_engine}")
        print(f"   Name: {db_name}")
        print(f"   Host: {db_host}")
        print(f"   Port: {db_port}")
        
    except Exception as e:
        print(f"❌ Could not retrieve database info: {e}")


if __name__ == "__main__":
    print("🔍 Testing MongoDB Connection for Contract Intelligence Parser")
    print("=" * 60)
    
    test_database_info()
    print()
    
    success = test_mongodb_connection()
    
    if success:
        print("\n🚀 MongoDB is ready for use!")
        sys.exit(0)
    else:
        print("\n💥 MongoDB setup failed. Please check your configuration.")
        sys.exit(1)

