#!/usr/bin/env python3
"""
Script to test database connection and list existing tables.
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.config import settings

def test_database_connection():
    """Test the database connection and list existing tables."""
    
    print("Testing Database Connection")
    print("=" * 40)
    
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        
        # Test connection
        with engine.connect() as connection:
            print("✅ Database connection successful!")
            
            # Get database info
            result = connection.execute(text("SELECT DATABASE()"))
            db_name = result.scalar()
            print(f"📊 Connected to database: {db_name}")
            
            # List existing tables
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            print(f"\n📋 Found {len(tables)} existing tables:")
            print("-" * 40)
            
            for i, table in enumerate(tables, 1):
                print(f"{i:2d}. {table}")
                
                # Get table info
                try:
                    columns = inspector.get_columns(table)
                    print(f"     Columns: {len(columns)}")
                    
                    # Show first few columns
                    for col in columns[:3]:
                        print(f"       - {col['name']}: {col['type']}")
                    if len(columns) > 3:
                        print(f"       ... and {len(columns) - 3} more columns")
                        
                except Exception as e:
                    print(f"     Error getting table info: {e}")
                
                print()
            
            # Check for our expected tables
            expected_tables = [
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
            
            print("🔍 Checking for expected Bogotá tables:")
            print("-" * 40)
            
            found_tables = []
            missing_tables = []
            
            for table in expected_tables:
                if table in tables:
                    found_tables.append(table)
                    print(f"✅ {table}")
                else:
                    missing_tables.append(table)
                    print(f"❌ {table} (missing)")
            
            print(f"\n📈 Summary:")
            print(f"   Found: {len(found_tables)}/{len(expected_tables)} expected tables")
            print(f"   Missing: {len(missing_tables)} tables")
            
            if missing_tables:
                print(f"\n⚠️  Missing tables: {', '.join(missing_tables)}")
            
        engine.dispose()
        
    except SQLAlchemyError as e:
        print(f"❌ Database connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_database_connection() 