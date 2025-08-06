#!/usr/bin/env python3
"""
Script to inspect the real structure of tables in the database.
"""

import os
import sys
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_database_connection():
    """Get database connection from environment variables."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        return connection
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

def inspect_table_structure(table_name):
    """Inspect the structure of a specific table."""
    connection = get_database_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor()
        
        # Get table structure
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        
        # Get table information
        cursor.execute(f"SHOW TABLE STATUS LIKE '{table_name}'")
        table_info = cursor.fetchone()
        
        return {
            'table_name': table_name,
            'columns': columns,
            'table_info': table_info
        }
        
    except Error as e:
        print(f"Error inspecting table {table_name}: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def inspect_all_tables():
    """Inspect all Bogotá tables."""
    connection = get_database_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        # Get all tables
        cursor.execute("SHOW TABLES")
        all_tables = [table[0] for table in cursor.fetchall()]
        
        # Filter Bogotá tables
        bogota_tables = [table for table in all_tables if 'bogota' in table.lower() or 'general_propietarios' in table.lower()]
        
        print("Bogotá Real Estate Database Structure Inspection")
        print("=" * 60)
        print(f"Found {len(bogota_tables)} Bogotá tables:")
        
        all_structures = {}
        
        for table in sorted(bogota_tables):
            print(f"\n📋 Table: {table}")
            print("-" * 40)
            
            structure = inspect_table_structure(table)
            if structure:
                all_structures[table] = structure
                
                print("Columns:")
                for column in structure['columns']:
                    field, type_info, null, key, default, extra = column
                    print(f"  - {field}: {type_info} {'(NULL)' if null == 'YES' else '(NOT NULL)'} {f'DEFAULT {default}' if default else ''}")
            else:
                print(f"❌ Could not inspect table {table}")
        
        return all_structures
        
    except Error as e:
        print(f"Error getting tables: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def generate_model_code(table_name, columns):
    """Generate SQLAlchemy model code for a table."""
    
    # SQLAlchemy type mapping
    type_mapping = {
        'int': 'Integer',
        'bigint': 'BigInteger',
        'varchar': 'String',
        'char': 'String',
        'text': 'Text',
        'longtext': 'Text',
        'mediumtext': 'Text',
        'tinytext': 'Text',
        'decimal': 'Numeric',
        'numeric': 'Numeric',
        'float': 'Float',
        'double': 'Float',
        'datetime': 'DateTime',
        'timestamp': 'DateTime',
        'date': 'Date',
        'time': 'Time',
        'year': 'Integer',
        'boolean': 'Boolean',
        'tinyint': 'Boolean',  # For boolean fields
        'json': 'JSON',
        'blob': 'LargeBinary',
        'longblob': 'LargeBinary',
        'mediumblob': 'LargeBinary',
        'tinyblob': 'LargeBinary',
    }
    
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
    
    for column in columns:
        field, type_info, null, key, default, extra = column
        
        # Parse type information
        base_type = type_info.split('(')[0].lower()
        sqlalchemy_type = type_mapping.get(base_type, 'String')
        
        # Handle specific cases
        if base_type == 'tinyint' and '1' in type_info:
            sqlalchemy_type = 'Boolean'
        elif base_type in ['decimal', 'numeric']:
            # Extract precision and scale
            if '(' in type_info and ')' in type_info:
                precision_scale = type_info.split('(')[1].split(')')[0]
                if ',' in precision_scale:
                    precision, scale = precision_scale.split(',')
                    sqlalchemy_type = f"Numeric({precision}, {scale})"
                else:
                    sqlalchemy_type = f"Numeric({precision_scale})"
            else:
                sqlalchemy_type = "Numeric"
        elif base_type == 'varchar' and '(' in type_info:
            # Extract length
            length = type_info.split('(')[1].split(')')[0]
            sqlalchemy_type = f"String({length})"
        elif base_type == 'char' and '(' in type_info:
            # Extract length
            length = type_info.split('(')[1].split(')')[0]
            sqlalchemy_type = f"String({length})"
        
        # Generate column definition
        nullable = "True" if null == 'YES' else "False"
        primary_key = "True" if key == 'PRI' else "False"
        index = "True" if key in ['MUL', 'UNI'] else "False"
        
        # Skip the id column if it's auto-increment (we have it in base)
        if field == 'id' and 'auto_increment' in extra.lower():
            continue
            
        model_code += f"    {field} = Column({sqlalchemy_type}, nullable={nullable}"
        
        if primary_key == "True":
            model_code += ", primary_key=True"
        if index == "True":
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
    print("Bogotá Real Estate Database - Real Structure Inspection")
    print("=" * 60)
    
    # Inspect all tables
    structures = inspect_all_tables()
    
    if not structures:
        print("❌ No tables found or connection failed")
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
            model_code = generate_model_code(table_name, structure['columns'])
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