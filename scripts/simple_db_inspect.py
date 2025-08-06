#!/usr/bin/env python3
"""
Simple script to inspect database structure using mysql.connector.
"""

import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def inspect_database():
    """Inspect the structure of Bogotá tables."""
    
    try:
        # Connect to database
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            print("Bogotá Real Estate Database Structure Inspection")
            print("=" * 60)
            
            # Get all tables
            cursor.execute("SHOW TABLES")
            all_tables = [table[0] for table in cursor.fetchall()]
            
            # Filter Bogotá tables
            bogota_tables = [table for table in all_tables if 'bogota' in table.lower() or 'general_propietarios' in table.lower()]
            
            print(f"Found {len(bogota_tables)} Bogotá tables:")
            print(", ".join(sorted(bogota_tables)))
            print()
            
            # Inspect each table
            for table in sorted(bogota_tables):
                print(f"📋 Table: {table}")
                print("-" * 40)
                
                # Get table structure
                cursor.execute(f"DESCRIBE {table}")
                columns = cursor.fetchall()
                
                print("Columns:")
                for column in columns:
                    field, type_info, null, key, default, extra = column
                    nullable = "(NULL)" if null == "YES" else "(NOT NULL)"
                    key_info = f" [{key}]" if key else ""
                    default_info = f" DEFAULT {default}" if default else ""
                    extra_info = f" {extra}" if extra else ""
                    
                    print(f"  - {field}: {type_info} {nullable}{key_info}{default_info}{extra_info}")
                
                print()
            
            cursor.close()
            connection.close()
            print("✅ Database inspection completed successfully!")
            
    except Error as e:
        print(f"❌ Error connecting to database: {e}")
        print("\nTroubleshooting:")
        print("1. Check your .env file has correct database credentials")
        print("2. Verify the database server is accessible")
        print("3. Check network connectivity to the Aurora endpoint")

if __name__ == "__main__":
    inspect_database() 