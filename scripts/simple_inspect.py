#!/usr/bin/env python3
"""
Simple script to inspect database structure.
"""

import os
import sys
import mysql.connector
from mysql.connector import Error

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def inspect_database():
    """Inspect the database structure."""
    
    try:
        # Database connection parameters
        host = os.getenv('DB_HOST')
        port = int(os.getenv('DB_PORT', 3306))
        user = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')
        database = os.getenv('DB_NAME')
        
        print(f"Connecting to database: {host}:{port}/{database}")
        
        # Create connection
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # List of tables to inspect
            tables = [
                'bogota_barmanpre_caracteristicas',
                'bogota_barmanpre_chip',
                'bogota_barmanpre_listings',
                'bogota_barmanpre_POT',
                'bogota_barmanpre_prediales_actuales',
                'bogota_barmanpre_prediales_totales',
                'bogota_barmanpre_proyectos',
                'bogota_barmanpre_transacciones',
                'bogota_barrio_dane',
                'bogota_barrio_listings',
                'bogota_bycode_listings',
                'bogota_bycode_listings_geometry',
                'bogota_bycodigo_proyectos',
                'bogota_chip_transacciones',
                'bogota_lotes_geometry',
                'bogota_lotes_normativa',
                'bogota_lotes_normativa_dict',
                'bogota_lotes_point',
                'bogota_propietarios_shd_historicos',
                'bogota_radio_barmanpre',
                'general_propietarios'
            ]
            
            print("\nDatabase Table Structure Inspection")
            print("=" * 50)
            
            for table_name in tables:
                print(f"\nTable: {table_name}")
                print("-" * 30)
                
                try:
                    # Get table structure
                    cursor.execute(f"DESCRIBE {table_name}")
                    columns = cursor.fetchall()
                    
                    for column in columns:
                        field_name = column[0]
                        field_type = column[1]
                        null_allowed = column[2]
                        key_type = column[3]
                        default_value = column[4]
                        extra = column[5]
                        
                        print(f"  {field_name}: {field_type} (nullable: {null_allowed})")
                        if key_type:
                            print(f"    Key: {key_type}")
                        if default_value:
                            print(f"    Default: {default_value}")
                        if extra:
                            print(f"    Extra: {extra}")
                    
                    # Get sample data count
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    print(f"  Total rows: {count}")
                    
                except Error as e:
                    print(f"  Error inspecting table: {e}")
            
            cursor.close()
            connection.close()
            print("\nDatabase connection closed.")
            
    except Error as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    inspect_database() 