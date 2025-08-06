#!/usr/bin/env python3
"""
Simple script to verify the file structure after refactoring.
"""

import os

def verify_structure():
    """Verify the file structure is correct."""
    
    print("Verifying File Structure")
    print("=" * 40)
    
    # Check main directories
    directories = [
        "app/models",
        "app/models/bogota_models",
    ]
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"✅ {directory}/")
        else:
            print(f"❌ {directory}/ (missing)")
    
    # Check main files
    main_files = [
        "app/models/__init__.py",
        "app/models/base.py",
        "app/models/bogota_models/__init__.py",
    ]
    
    print("\nMain Files:")
    for file_path in main_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} (missing)")
    
    # Check individual model files
    model_files = [
        "barmanpre_caracteristicas.py",
        "barmanpre_chip.py",
        "barmanpre_listings.py",
        "barmanpre_pot.py",
        "barmanpre_prediales_actuales.py",
        "barmanpre_prediales_totales.py",
        "barmanpre_proyectos.py",
        "barmanpre_transacciones.py",
        "barrio_dane.py",
        "barrio_listings.py",
        "bycode_listings.py",
        "bycode_listings_geometry.py",
        "bycodigo_proyectos.py",
        "chip_transacciones.py",
        "lotes_geometry.py",
        "lotes_normativa.py",
        "lotes_normativa_dict.py",
        "lotes_point.py",
        "propietarios_shd_historicos.py",
        "radio_barmanpre.py",
        "general_propietarios.py",
    ]
    
    print(f"\nIndividual Model Files ({len(model_files)} total):")
    missing_files = []
    for filename in model_files:
        file_path = f"app/models/bogota_models/{filename}"
        if os.path.exists(file_path):
            print(f"✅ {filename}")
        else:
            print(f"❌ {filename} (missing)")
            missing_files.append(filename)
    
    # Summary
    print(f"\nSummary:")
    print(f"✅ Found: {len(model_files) - len(missing_files)}/{len(model_files)} model files")
    if missing_files:
        print(f"❌ Missing: {len(missing_files)} files")
        print(f"   Missing files: {', '.join(missing_files)}")
    else:
        print("🎉 All files present!")
    
    # Check that the old file is gone
    if os.path.exists("app/models/bogota_models.py"):
        print("⚠️  Warning: Old consolidated file still exists")
    else:
        print("✅ Old consolidated file removed")

if __name__ == "__main__":
    verify_structure() 