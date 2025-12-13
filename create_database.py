#!/usr/bin/env python
"""
Script to create the MySQL database for FusionTec Django project
"""

import MySQLdb
from django.conf import settings
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fusiontec.settings')
django.setup()

from django.conf import settings

def create_database():
    """Create the MySQL database if it doesn't exist"""
    
    db_config = settings.DATABASES['default']
    db_name = db_config['NAME']
    db_user = db_config['USER']
    db_password = db_config['PASSWORD']
    db_host = db_config['HOST']
    db_port = int(db_config['PORT'])
    
    print(f"Connecting to MySQL server at {db_host}:{db_port}...")
    
    try:
        # Connect to MySQL server (without specifying database)
        connection = MySQLdb.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            passwd=db_password
        )
        
        cursor = connection.cursor()
        
        # Check if database exists
        cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
        result = cursor.fetchone()
        
        if result:
            print(f"Database '{db_name}' already exists.")
        else:
            # Create database
            print(f"Creating database '{db_name}'...")
            cursor.execute(f"CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"Database '{db_name}' created successfully!")
        
        cursor.close()
        connection.close()
        
        return True
        
    except MySQLdb.Error as e:
        print(f"Error: {e}")
        print(f"\nMake sure:")
        print(f"   1. MySQL server is running")
        print(f"   2. User '{db_user}' has CREATE DATABASE privileges")
        print(f"   3. Password is correct")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = create_database()
    if success:
        print("\nDatabase setup complete! You can now run migrations:")
        print("   python manage.py migrate")
    sys.exit(0 if success else 1)

