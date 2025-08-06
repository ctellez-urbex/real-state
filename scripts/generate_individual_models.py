#!/usr/bin/env python3
"""
Script to generate individual model files from the consolidated bogota_models.py file.
"""

import os
import re

def extract_model_class(content, class_name):
    """Extract a specific model class from the content."""
    pattern = rf"class {class_name}\(Base\):.*?def __repr__\(self\) -> str:.*?return f.*?\)>"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(0)
    return None

def generate_model_file(class_name, class_content, table_name):
    """Generate individual model file."""
    
    # Extract imports from the original content
    imports = """from sqlalchemy import Column, String, Integer, Float, Text, Boolean, Numeric, DateTime, Date, JSON
from ..base import Base

"""
    
    # Create the file content
    file_content = f'''"""
{class_name} model for Bogotá.
"""

{imports}

{class_content}
'''
    
    # Create filename
    filename = f"app/models/bogota_models/{table_name.lower()}.py"
    
    # Write file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(file_content)
    
    print(f"✅ Created: {filename}")

def main():
    """Generate all individual model files."""
    
    # Read the original consolidated file
    with open('app/models/bogota_models.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define the models to extract
    models_to_extract = [
        ("BogotaBarmanprePredialesTotales", "barmanpre_prediales_totales"),
        ("BogotaBarmanpreProyectos", "barmanpre_proyectos"),
        ("BogotaBarrioListings", "barrio_listings"),
        ("BogotaBycodeListings", "bycode_listings"),
        ("BogotaBycodeListingsGeometry", "bycode_listings_geometry"),
        ("BogotaBycodigoProyectos", "bycodigo_proyectos"),
        ("BogotaChipTransacciones", "chip_transacciones"),
        ("BogotaLotesGeometry", "lotes_geometry"),
        ("BogotaLotesNormativa", "lotes_normativa"),
        ("BogotaLotesNormativaDict", "lotes_normativa_dict"),
        ("BogotaLotesPoint", "lotes_point"),
        ("BogotaPropietariosShdHistoricos", "propietarios_shd_historicos"),
        ("BogotaRadioBarmanpre", "radio_barmanpre"),
        ("GeneralPropietarios", "general_propietarios"),
    ]
    
    print("Generating individual model files...")
    print("=" * 50)
    
    for class_name, table_name in models_to_extract:
        class_content = extract_model_class(content, class_name)
        if class_content:
            generate_model_file(class_name, class_content, table_name)
        else:
            print(f"❌ Could not extract: {class_name}")
    
    print("\n✅ All individual model files generated!")
    print("\nNext steps:")
    print("1. Delete the original app/models/bogota_models.py file")
    print("2. Update alembic/env.py to import from the new structure")
    print("3. Test the imports")

if __name__ == "__main__":
    main() 