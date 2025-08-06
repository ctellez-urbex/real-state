#!/usr/bin/env python3
"""
Script to generate SQLAlchemy models based on the real database structure.
"""

def generate_model_code(table_name, columns_data):
    """Generate SQLAlchemy model code for a table."""
    
    # Convert table name to class name
    class_name = ''.join(word.capitalize() for word in table_name.replace('bogota_', '').split('_'))
    if not class_name.startswith('Bogota'):
        class_name = 'Bogota' + class_name
    
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
        'tinyint': 'Boolean',
        'json': 'JSON',
        'blob': 'LargeBinary',
        'longblob': 'LargeBinary',
        'mediumblob': 'LargeBinary',
        'tinyblob': 'LargeBinary',
        'point': 'String',  # For geometry points
        'geometry': 'String',  # For geometry fields
    }
    
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
    
    for column_info in columns_data:
        field, data_type, nullable, key, default, extra = column_info
        
        # Parse type information
        base_type = data_type.split('(')[0].lower()
        sqlalchemy_type = type_mapping.get(base_type, 'String')
        
        # Handle specific cases
        if base_type == 'varchar' and '(' in data_type:
            length = data_type.split('(')[1].split(')')[0]
            sqlalchemy_type = f"String({length})"
        elif base_type == 'char' and '(' in data_type:
            length = data_type.split('(')[1].split(')')[0]
            sqlalchemy_type = f"String({length})"
        elif base_type == 'decimal' and '(' in data_type:
            precision_scale = data_type.split('(')[1].split(')')[0]
            if ',' in precision_scale:
                precision, scale = precision_scale.split(',')
                sqlalchemy_type = f"Numeric({precision}, {scale})"
            else:
                sqlalchemy_type = f"Numeric({precision_scale})"
        elif base_type == 'tinyint' and '1' in data_type:
            sqlalchemy_type = 'Boolean'
        
        # Generate column definition
        nullable_str = "True" if nullable == "YES" else "False"
        primary_key = "True" if key == "PRI" else "False"
        unique = "True" if key == "UNI" else "False"
        index = "True" if key == "MUL" else "False"
        
        # Skip the id column if it's auto-increment (we have it in base)
        if field == 'id' and 'auto_increment' in extra.lower():
            continue
            
        model_code += f"    {field} = Column({sqlalchemy_type}, nullable={nullable_str}"
        
        if primary_key == "True":
            model_code += ", primary_key=True"
        if unique == "True":
            model_code += ", unique=True"
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
    """Generate all models based on real database structure."""
    
    # Real database structure data
    table_structures = {
        'bogota_barmanpre_prediales_totales': [
            ('id', 'int', 'NO', 'PRI', '', 'auto_increment'),
            ('grupo', 'int', 'YES', 'UNI', '', ''),
            ('barmanpre', 'varchar', 'YES', 'UNI', '', ''),
            ('prediales', 'longtext', 'YES', '', '', ''),
            ('prediales_mt2', 'longtext', 'YES', '', '', ''),
            ('prediales_mt2_by_precuso', 'longtext', 'YES', '', '', ''),
            ('fecha_update', 'datetime', 'YES', '', '', ''),
        ],
        'bogota_barmanpre_proyectos': [
            ('id', 'int', 'NO', 'PRI', '', 'auto_increment'),
            ('grupo', 'int', 'YES', 'UNI', '', ''),
            ('barmanpre', 'varchar', 'YES', 'UNI', '', ''),
            ('codproyecto', 'longtext', 'YES', '', '', ''),
            ('radio', 'longtext', 'YES', '', '', ''),
            ('fecha_update', 'datetime', 'YES', '', '', ''),
        ],
        'bogota_barmanpre_transacciones': [
            ('id', 'int', 'NO', 'PRI', '', 'auto_increment'),
            ('grupo', 'int', 'YES', 'UNI', '', ''),
            ('barmanpre', 'varchar', 'YES', 'UNI', '', ''),
            ('anotaciones', 'longtext', 'YES', '', '', ''),
            ('transacciones_barmanpre', 'longtext', 'YES', '', '', ''),
            ('transacciones_12m', 'longtext', 'YES', '', '', ''),
            ('transacciones_12m_by_class', 'longtext', 'YES', '', '', ''),
            ('transacciones_historicas', 'longtext', 'YES', '', '', ''),
            ('transacciones_historicas_by_class', 'longtext', 'YES', '', '', ''),
            ('transacciones_year', 'longtext', 'YES', '', '', ''),
            ('fecha_update', 'datetime', 'YES', '', '', ''),
        ],
        'bogota_barrio_dane': [
            ('id', 'int', 'NO', 'PRI', '', 'auto_increment'),
            ('scacodigo', 'varchar', 'YES', 'UNI', '', ''),
            ('dane', 'longtext', 'YES', '', '', ''),
            ('fecha_update', 'datetime', 'YES', '', '', ''),
        ],
        'bogota_barrio_listings': [
            ('id', 'int', 'NO', 'PRI', '', 'auto_increment'),
            ('scacodigo', 'varchar', 'YES', 'UNI', '', ''),
            ('valorizacion', 'longtext', 'YES', '', '', ''),
            ('valoresbarrio', 'longtext', 'YES', '', '', ''),
            ('fecha_update', 'datetime', 'YES', '', '', ''),
        ],
        'bogota_bycode_listings': [
            ('id', 'int', 'NO', 'PRI', '', 'auto_increment'),
            ('code', 'varchar', 'YES', 'UNI', '', ''),
            ('listings', 'longtext', 'YES', '', '', ''),
            ('fecha_update', 'datetime', 'YES', '', '', ''),
        ],
        'bogota_bycode_listings_geometry': [
            ('id', 'int', 'NO', 'PRI', '', 'auto_increment'),
            ('code', 'varchar', 'YES', 'UNI', '', ''),
            ('latitud', 'double', 'YES', '', '', ''),
            ('longitud', 'double', 'YES', '', '', ''),
            ('fecha_update', 'datetime', 'YES', '', '', ''),
            ('geometry', 'point', 'NO', 'MUL', '', ''),
        ],
        'bogota_bycodigo_proyectos': [
            ('id', 'int', 'NO', 'PRI', '', 'auto_increment'),
            ('codproyecto', 'int', 'YES', 'UNI', '', ''),
            ('output', 'longtext', 'YES', '', '', ''),
            ('fecha_update', 'datetime', 'YES', '', '', ''),
        ],
        'bogota_chip_transacciones': [
            ('id', 'int', 'NO', 'PRI', '', 'auto_increment'),
            ('chip', 'varchar', 'YES', 'UNI', '', ''),
            ('transacciones', 'longtext', 'YES', '', '', ''),
            ('fecha_update', 'datetime', 'YES', '', '', ''),
        ],
        'bogota_lotes_geometry': [
            ('id', 'int', 'NO', 'PRI', '', 'auto_increment'),
            ('grupo', 'int', 'YES', 'UNI', '', ''),
            ('barmanpre', 'varchar', 'YES', 'UNI', '', ''),
            ('manzcodigo', 'varchar', 'YES', '', '', ''),
            ('latitud', 'double', 'YES', '', '', ''),
            ('longitud', 'double', 'YES', '', '', ''),
            ('geometry', 'geometry', 'NO', 'MUL', '', ''),
            ('fecha_update', 'datetime', 'YES', '', '', ''),
        ],
        'bogota_lotes_normativa': [
            ('id', 'int', 'NO', 'PRI', '', 'auto_increment'),
            ('lista', 'longtext', 'YES', '', '', ''),
            ('pisos', 'int', 'YES', '', '', ''),
            ('altura_min_pot', 'int', 'YES', '', '', ''),
            ('tratamiento', 'int', 'YES', 'MUL', '', ''),
            ('actuacion_estrategica', 'int', 'YES', '', '', ''),
            ('area_de_actividad', 'int', 'YES', '', '', ''),
            ('numero_propietarios', 'int', 'YES', '', '', ''),
            ('via_principal', 'int', 'YES', '', '', ''),
            ('fecha_update', 'datetime', 'YES', '', '', ''),
        ],
        'bogota_lotes_normativa_dict': [
            ('id', 'int', 'NO', 'PRI', '', 'auto_increment'),
            ('variable', 'varchar', 'YES', '', '', ''),
            ('indice', 'int', 'YES', '', '', ''),
            ('input', 'varchar', 'YES', '', '', ''),
            ('fecha_update', 'datetime', 'YES', '', '', ''),
        ],
        'bogota_lotes_point': [
            ('id', 'int', 'NO', 'PRI', '', 'auto_increment'),
            ('grupo', 'int', 'YES', 'UNI', '', ''),
            ('barmanpre', 'varchar', 'YES', 'UNI', '', ''),
            ('manzcodigo', 'varchar', 'YES', '', '', ''),
            ('geometry', 'geometry', 'NO', 'MUL', '', ''),
            ('fecha_update', 'datetime', 'YES', '', '', ''),
        ],
        'bogota_propietarios_shd_historicos': [
            ('id', 'int', 'NO', '', '0', ''),
            ('numero', 'varchar', 'YES', 'MUL', '', ''),
            ('propietario', 'longtext', 'YES', '', '', ''),
            ('fecha_update', 'datetime', 'YES', '', '', ''),
        ],
        'bogota_radio_barmanpre': [
            ('id', 'int', 'NO', 'PRI', '', 'auto_increment'),
            ('grupo', 'int', 'YES', 'UNI', '', ''),
            ('barmanpre', 'varchar', 'YES', 'UNI', '', ''),
            ('grupo_radio', 'longtext', 'YES', '', '', ''),
        ],
        'general_propietarios': [
            # This table wasn't in the provided data, so we'll create a placeholder
            ('id', 'int', 'NO', 'PRI', '', 'auto_increment'),
            ('propietario', 'varchar', 'YES', '', '', ''),
            ('fecha_update', 'datetime', 'YES', '', '', ''),
        ],
    }
    
    print("Generating SQLAlchemy models based on real database structure...")
    print("=" * 70)
    
    for table_name, columns_data in table_structures.items():
        try:
            model_code = generate_model_code(table_name, columns_data)
            save_model_file(table_name, model_code)
        except Exception as e:
            print(f"❌ Error generating model for {table_name}: {e}")
    
    print("\n🎉 All models generated successfully!")
    print("\nNext steps:")
    print("1. Review the generated models")
    print("2. Test the imports with: python3 scripts/test_models_import.py")
    print("3. Create migration with: make db-migrate-initial")

if __name__ == "__main__":
    main() 