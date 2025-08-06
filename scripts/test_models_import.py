#!/usr/bin/env python3
"""
Script to test that all models can be imported correctly.
"""

import os
import sys

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_model_imports():
    """Test that all models can be imported correctly."""
    
    print("Testing Model Imports")
    print("=" * 40)
    
    try:
        # Test base model
        print("Testing base model...")
        from app.models.base import Base
        print("✅ Base model imported successfully")
        
        # Test individual models
        print("\nTesting individual models...")
        from app.models.bogota import (
            BogotaDataAndenes,
            BogotaBarmanpreChip,
            BogotaBarmanpreListings,
            BogotaBarmanprePOT,
            BogotaBarmanprePredialesActuales,
            BogotaBarmanprePredialesTotales,
            BogotaBarmanpreProyectos,
            BogotaBarmanpreTransacciones,
            BogotaBarrioDane,
            BogotaBarrioListings,
            BogotaBycodeListings,
            BogotaBycodeListingsGeometry,
            BogotaBycodigoProyectos,
            BogotaChipTransacciones,
            BogotaLotesGeometry,
            BogotaLotesNormativa,
            BogotaLotesNormativaDict,
            BogotaLotesPoint,
            BogotaPropietariosShdHistoricos,
            BogotaRadioBarmanpre,
            GeneralPropietarios,
        )
        print("✅ All individual models imported successfully")
        
        # Test main models module
        print("\nTesting main models module...")
        from app.models import (
            BogotaDataAndenes,
            BogotaBarmanpreChip,
            BogotaBarmanpreListings,
            BogotaBarmanprePOT,
            BogotaBarmanprePredialesActuales,
            BogotaBarmanprePredialesTotales,
            BogotaBarmanpreProyectos,
            BogotaBarmanpreTransacciones,
            BogotaBarrioDane,
            BogotaBarrioListings,
            BogotaBycodeListings,
            BogotaBycodeListingsGeometry,
            BogotaBycodigoProyectos,
            BogotaChipTransacciones,
            BogotaLotesGeometry,
            BogotaLotesNormativa,
            BogotaLotesNormativaDict,
            BogotaLotesPoint,
            BogotaPropietariosShdHistoricos,
            BogotaRadioBarmanpre,
            GeneralPropietarios,
        )
        print("✅ Main models module imported successfully")
        
        # Test SQLAlchemy metadata
        print("\nTesting SQLAlchemy metadata...")
        from app.models import Base
        tables = Base.metadata.tables.keys()
        print(f"✅ Found {len(tables)} tables in metadata:")
        for table in sorted(tables):
            print(f"   - {table}")
        
        print("\n🎉 All model imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_individual_model_files():
    """Test that all individual model files exist."""
    
    print("\nTesting Individual Model Files")
    print("=" * 40)
    
    expected_files = [
        "app/models/bogota/data_andenes.py",
        "app/models/bogota/data_barrio_catastral.py",
        
    ]
    
    missing_files = []
    for file_path in expected_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} (missing)")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Missing {len(missing_files)} files")
        return False
    else:
        print(f"\n✅ All {len(expected_files)} model files exist")
        return True

if __name__ == "__main__":
    print("Bogotá Real Estate Models - Import Test")
    print("=" * 50)
    
    # Test individual files
    files_ok = test_individual_model_files()
    
    # Test imports
    imports_ok = test_model_imports()
    
    if files_ok and imports_ok:
        print("\n🎉 All tests passed! Models are ready to use.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.") 