#!/usr/bin/env python3
"""
Script to inspect the real structure of tables using SQLAlchemy.
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.config import settings

def get_database_engine():
    """Get database engine from settings."""
    try:
        engine = create_engine(settings.DATABASE_URL)
        return engine
    except Exception as e:
        print(f"Error creating database engine: {e}")
        return None

def inspect_table_structure(engine, table_name):
    """Inspect the structure of a specific table using SQLAlchemy."""
    try:
        inspector = inspect(engine)
        
        # Get columns
        columns = inspector.get_columns(table_name)
        
        # Get primary keys
        primary_keys = inspector.get_pk_constraint(table_name)
        
        # Get indexes
        indexes = inspector.get_indexes(table_name)
        
        return {
            'table_name': table_name,
            'columns': columns,
            'primary_keys': primary_keys,
            'indexes': indexes
        }
        
    except Exception as e:
        print(f"Error inspecting table {table_name}: {e}")
        return None

def inspect_all_tables():
    """Inspect all Bogotá tables."""
    engine = get_database_engine()
    if not engine:
        return None
    
    try:
        inspector = inspect(engine)
        
        # Get all tables
        all_tables = inspector.get_table_names()
        
        # Filter Bogotá tables
        bogota_tables = [table for table in all_tables if 'bogota' in table.lower() or 'general_propietarios' in table.lower()]
        
        print("Bogotá Real Estate Database Structure Inspection")
        print("=" * 60)
        print(f"Found {len(bogota_tables)} Bogotá tables:")
        
        all_structures = {}
        
        for table in sorted(bogota_tables):
            print(f"\n📋 Table: {table}")
            print("-" * 40)
            
            structure = inspect_table_structure(engine, table)
            if structure:
                all_structures[table] = structure
                
                print("Columns:")
                for column in structure['columns']:
                    name = column['name']
                    type_info = str(column['type'])
                    nullable = column.get('nullable', True)
                    default = column.get('default', None)
                    
                    print(f"  - {name}: {type_info} {'(NULL)' if nullable else '(NOT NULL)'} {f'DEFAULT {default}' if default else ''}")
                
                # Show primary keys
                if structure['primary_keys']['constrained_columns']:
                    print(f"  Primary Keys: {', '.join(structure['primary_keys']['constrained_columns'])}")
                
                # Show indexes
                if structure['indexes']:
                    print(f"  Indexes: {len(structure['indexes'])} found")
            else:
                print(f"❌ Could not inspect table {table}")
        
        return all_structures
        
    except Exception as e:
        print(f"Error getting tables: {e}")
        return None
    finally:
        engine.dispose()

def generate_model_code(table_name, structure):
    """Generate SQLAlchemy model code for a table."""
    
    # Convert table name to class name
    class_name = ''.join(word.capitalize() for word in table_name.replace('bogota_', '').split('_'))
    if not class_name.startswith('Bogota'):
        class_name = 'Bogota' + class_name
    
    # Generate model code
    model_code = f'''"""
{class_name} model for Bogotá.
"""

from sqlalchemy import Column, String, Integer, Float, Text, Boolean, Numeric, DateTime, Date, JSON, BigInteger
from ..base import Base


class {class_name}(Base):
    """{table_name} table."""
    
    __tablename__ = "{table_name}"
    
'''
    
    for column in structure['columns']:
        name = column['name']
        type_info = column['type']
        nullable = column.get('nullable', True)
        default = column.get('default', None)
        
        # Convert SQLAlchemy type to Column definition
        sqlalchemy_type = str(type_info)
        
        # Handle specific type conversions
        if 'VARCHAR' in sqlalchemy_type:
            # Extract length from VARCHAR(length)
            if '(' in sqlalchemy_type and ')' in sqlalchemy_type:
                length = sqlalchemy_type.split('(')[1].split(')')[0]
                sqlalchemy_type = f"String({length})"
            else:
                sqlalchemy_type = "String"
        elif 'CHAR' in sqlalchemy_type:
            if '(' in sqlalchemy_type and ')' in sqlalchemy_type:
                length = sqlalchemy_type.split('(')[1].split(')')[0]
                sqlalchemy_type = f"String({length})"
            else:
                sqlalchemy_type = "String"
        elif 'DECIMAL' in sqlalchemy_type or 'NUMERIC' in sqlalchemy_type:
            if '(' in sqlalchemy_type and ')' in sqlalchemy_type:
                precision_scale = sqlalchemy_type.split('(')[1].split(')')[0]
                if ',' in precision_scale:
                    precision, scale = precision_scale.split(',')
                    sqlalchemy_type = f"Numeric({precision}, {scale})"
                else:
                    sqlalchemy_type = f"Numeric({precision_scale})"
            else:
                sqlalchemy_type = "Numeric"
        elif 'TINYINT' in sqlalchemy_type:
            sqlalchemy_type = "Boolean"
        elif 'INT' in sqlalchemy_type and 'BIGINT' not in sqlalchemy_type:
            sqlalchemy_type = "Integer"
        elif 'BIGINT' in sqlalchemy_type:
            sqlalchemy_type = "BigInteger"
        elif 'FLOAT' in sqlalchemy_type or 'DOUBLE' in sqlalchemy_type:
            sqlalchemy_type = "Float"
        elif 'DATETIME' in sqlalchemy_type or 'TIMESTAMP' in sqlalchemy_type:
            sqlalchemy_type = "DateTime"
        elif 'DATE' in sqlalchemy_type:
            sqlalchemy_type = "Date"
        elif 'TEXT' in sqlalchemy_type:
            sqlalchemy_type = "Text"
        elif 'JSON' in sqlalchemy_type:
            sqlalchemy_type = "JSON"
        
        # Skip the id column if it's auto-increment (we have it in base)
        if name == 'id' and 'auto_increment' in str(type_info).lower():
            continue
            
        # Check if it's a primary key
        is_primary_key = name in structure['primary_keys']['constrained_columns']
        
        # Check if it has an index
        has_index = any(name in idx['column_names'] for idx in structure['indexes'])
        
        model_code += f"    {name} = Column({sqlalchemy_type}, nullable={nullable}"
        
        if is_primary_key:
            model_code += ", primary_key=True"
        if has_index:
            model_code += ", index=True"
        if default and default != 'NULL':
            if isinstance(default, str) and not default.isdigit():
                model_code += f', default="{default}"'
            else:
                model_code += f', default={default}'
        
        model_code += ")\n"
    
    model_code += f'''
    def __repr__(self) -> str:
        return f"<{class_name}(id={{self.id}})>"
'''
    
    return model_code

def save_model_file(table_name, model_code):
    """Save model code to file."""
    # Convert table name to filename
    filename = table_name.replace('bogota_', '').replace('_', '_')
    filepath = f"app/models/bogota_models/{filename}.py"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(model_code)
    
    print(f"✅ Generated: {filepath}")

def main():
    """Main function to inspect and generate models."""
    print("Bogotá Real Estate Database - Real Structure Inspection (SQLAlchemy)")
    print("=" * 70)
    
    # Inspect all tables
    structures = inspect_all_tables()
    
    if not structures:
        print("❌ No tables found or connection failed")
        print("\nTroubleshooting:")
        print("1. Check your .env file has correct database credentials")
        print("2. Verify database connection with: make test-db")
        print("3. Check if the database server is accessible")
        return
    
    # Ask user if they want to generate models
    response = input("\nDo you want to generate SQLAlchemy models based on the real structure? (y/n): ")
    if response.lower() not in ['y', 'yes']:
        print("Model generation cancelled.")
        return
    
    print("\nGenerating SQLAlchemy models...")
    print("=" * 40)
    
    for table_name, structure in structures.items():
        try:
            model_code = generate_model_code(table_name, structure)
            save_model_file(table_name, model_code)
        except Exception as e:
            print(f"❌ Error generating model for {table_name}: {e}")
    
    print("\n🎉 Model generation complete!")
    print("\nNext steps:")
    print("1. Review the generated models")
    print("2. Update app/models/bogota_models/__init__.py if needed")
    print("3. Test the imports with: python3 scripts/test_models_import.py")

if __name__ == "__main__":
    main() 