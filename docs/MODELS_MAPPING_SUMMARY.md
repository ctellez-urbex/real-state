# Models Mapping Summary

## ✅ Implemented Models (Connected to Real Database)

| Model | Table Name | Records | Status |
|-------|------------|---------|--------|
| `BogotaDataAndenes` | `bogota_data_andenes` | 164,956 | ✅ Implemented |
| `BogotaDataBarrioCatastral` | `bogota_data_barrio_catastral` | 1,205 | ✅ Implemented |
| `BogotaDataCalzada` | `bogota_data_calzada` | 101,871 | ✅ Implemented |
| `BogotaDataCaracteristicas` | `bogota_data_caracteristicas` | 924,445 | ✅ Implemented |
| `BogotaLotesNormativa` | `bogota_lotes_normativa` | 33,065 | ✅ Implemented |
| `BogotaLotesNormativaDict` | `bogota_lotes_normativa_dict` | 36 | ✅ Implemented |

## 📋 Model Details

### BogotaDataAndenes
- **Purpose**: Contains andenes (sidewalk) information for lots in Bogotá
- **Key Columns**: `id`, `andenes`, `andcodigo`, `andciv`, `fecha_update`
- **Geometry**: No

### BogotaDataBarrioCatastral
- **Purpose**: Contains neighborhood (barrio) information with geometry
- **Key Columns**: `id`, `scacodigo`, `scatipo`, `scanombre`, `geometry`
- **Geometry**: ✅ Yes (Polygon)

### BogotaDataCalzada
- **Purpose**: Contains road/street information with geometry
- **Key Columns**: `id`, `calfuncion`, `caltsuperf`, `calcodigo`, `calancho`, `callongitu`, `geometry`
- **Geometry**: ✅ Yes (LineString)

### BogotaDataCaracteristicas
- **Purpose**: Contains property characteristics and cadastral data
- **Key Columns**: `id`, `barmanpre`, `preaconst`, `preaterre`, `estrato`, `formato_direccion`
- **Geometry**: No

### BogotaLotesNormativa
- **Purpose**: Contains normative information for lots
- **Key Columns**: `id`, `lista`, `pisos`, `altura_min_pot`, `tratamiento`, `actuacion_estrategica`
- **Geometry**: No

### BogotaLotesNormativaDict
- **Purpose**: Contains dictionary mappings for normative variables
- **Key Columns**: `id`, `variable`, `indice`, `input_value`, `fecha_update`
- **Geometry**: No

## 🔧 Technical Implementation

### Dependencies
- `sqlalchemy==2.0.23`
- `geoalchemy2==0.18.0` (for geometry support)
- `mysql-connector-python==8.3.0`

### Import Structure
```python
from app.models import (
    BogotaDataAndenes,
    BogotaDataBarrioCatastral,
    BogotaDataCalzada,
    BogotaDataCaracteristicas,
    BogotaLotesNormativa,
    BogotaLotesNormativaDict
)
```

### Optimized __repr__ Method
All models use the optimized `_format_attrs()` method for fast and complete string representation:

```python
def __repr__(self):
    return f"<ModelName({self._format_attrs()})>"

def _format_attrs(self):
    return ', '.join(f"{col.name}={getattr(self, col.name)}" 
                    for col in self.__table__.columns)
```

## 🚀 Usage Example

```python
from app.models import BogotaDataCaracteristicas
from app.core.database import get_db

# Get database session
db = get_db()

# Query properties
properties = db.query(BogotaDataCaracteristicas).filter(
    BogotaDataCaracteristicas.estrato == 3
).limit(10).all()

# Print with full representation
for prop in properties:
    print(prop)  # Shows all columns automatically
```

## 📊 Database Connection Status
- ✅ All models successfully import
- ✅ All models connect to real database tables
- ✅ All models have optimized `__repr__` methods
- ✅ Geometry support enabled with GeoAlchemy2 