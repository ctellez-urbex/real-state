#!/usr/bin/env python3
"""
Script to inspect the structure of existing database tables.
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.config import settings

def inspect_table_structure():
    """Inspect the structure of all tables in the database."""
    
    # Create database engine
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)
    
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
    
    print("Database Table Structure Inspection")
    print("=" * 50)
    
    for table_name in tables:
        print(f"\nTable: {table_name}")
        print("-" * 30)
        
        try:
            # Get columns
            columns = inspector.get_columns(table_name)
            for column in columns:
                print(f"  {column['name']}: {column['type']} (nullable: {column['nullable']})")
            
            # Get primary keys
            pk = inspector.get_pk_constraint(table_name)
            if pk['constrained_columns']:
                print(f"  Primary Key: {', '.join(pk['constrained_columns'])}")
            
            # Get foreign keys
            fks = inspector.get_foreign_keys(table_name)
            for fk in fks:
                print(f"  Foreign Key: {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
            
            # Get indexes
            indexes = inspector.get_indexes(table_name)
            for index in indexes:
                print(f"  Index: {index['name']} on {index['column_names']} (unique: {index['unique']})")
                
        except Exception as e:
            print(f"  Error inspecting table: {e}")
    
    engine.dispose()

if __name__ == "__main__":
    inspect_table_structure() 