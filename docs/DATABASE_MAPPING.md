# Mapeo de Base de Datos MySQL Aurora AWS - Bogotá Real Estate

Este documento describe el mapeo completo de la base de datos MySQL Aurora AWS para el proyecto de bienes raíces de Bogotá.

## 📋 Estructura de Modelos

El proyecto sigue las **buenas prácticas** de tener **un modelo por archivo** para mejor organización y mantenibilidad. **Todos los modelos están basados en la estructura real de la base de datos**:

```
app/models/
├── __init__.py                 # Exporta todos los modelos
├── base.py                     # Modelo base con campos comunes
└── bogota_models/              # Módulo de modelos de Bogotá
    ├── __init__.py             # Exporta todos los modelos de Bogotá
    ├── barmanpre_chip.py       # Identificación catastral (CHIP)
    ├── barmanpre_listings.py   # Listados de propiedades
    ├── barmanpre_caracteristicas.py  # Características de propiedades
    ├── barmanpre_transacciones.py    # Transacciones
    ├── barmanpre_pot.py        # Plan de Ordenamiento Territorial
    ├── barmanpre_prediales_actuales.py  # Prediales actuales
    ├── barmanpre_prediales_totales.py   # Historial de prediales
    ├── barmanpre_proyectos.py  # Proyectos inmobiliarios
    ├── barrio_dane.py          # Códigos de barrios DANE
    ├── barrio_listings.py      # Resumen por barrio
    ├── bycode_listings.py      # Listados por código
    ├── bycode_listings_geometry.py  # Geometría de listados
    ├── bycodigo_proyectos.py   # Proyectos por código
    ├── chip_transacciones.py   # Transacciones por CHIP
    ├── lotes_geometry.py       # Geometría de lotes
    ├── lotes_normativa.py      # Normativa de lotes
    ├── lotes_normativa_dict.py # Diccionario de normativas
    ├── lotes_point.py          # Puntos de lotes
    ├── propietarios_shd_historicos.py  # Historial de propietarios
    ├── radio_barmanpre.py      # Datos de radio
    └── general_propietarios.py # Propietarios generales
```

## 🏠 Tablas Mapeadas (22 modelos)

### 🏠 Tablas de Propiedades (Barmanpre)
- `BogotaBarmanpreCaracteristicas` - Características de propiedades (catastro_predios, general_catastro, etc.)
- `BogotaBarmanpreChip` - Identificación catastral (CHIP, latitud, longitud)
- `BogotaBarmanpreListings` - Listados de propiedades (code_activo_radio, code_activo_barmanpre)
- `BogotaBarmanprePOT` - Plan de Ordenamiento Territorial (POT data)
- `BogotaBarmanprePredialesActuales` - Prediales actuales (prediales, prediales_mt2)
- `BogotaBarmanprePredialesTotales` - Historial de prediales (prediales, prediales_mt2)
- `BogotaBarmanpreProyectos` - Proyectos inmobiliarios (codproyecto, radio)
- `BogotaBarmanpreTransacciones` - Transacciones de propiedades (transacciones_barmanpre, transacciones_12m)

### 🏘️ Tablas de Barrios y Ubicaciones
- `BogotaBarrioDane` - Códigos de barrios DANE (scacodigo, dane)
- `BogotaBarrioListings` - Resumen de listados por barrio (valorizacion, valoresbarrio)

### 📍 Tablas de Códigos y Geometría
- `BogotaBycodeListings` - Listados por código de propiedad (code, listings)
- `BogotaBycodeListingsGeometry` - Datos geométricos de listados (latitud, longitud, geometry)
- `BogotaBycodigoProyectos` - Proyectos por código (codproyecto, output)
- `BogotaChipTransacciones` - Transacciones por CHIP (chip, transacciones)

### 🗺️ Tablas de Lotes y Normativa
- `BogotaLotesGeometry` - Geometría de lotes (manzcodigo, latitud, longitud, geometry)
- `BogotaLotesNormativa` - Normativa de lotes (lista, pisos, altura_min_pot, tratamiento)
- `BogotaLotesNormativaDict` - Diccionario de normativas (variable, indice, input)
- `BogotaLotesPoint` - Datos de puntos de lotes (manzcodigo, geometry)

### 👥 Tablas de Propietarios
- `BogotaPropietariosShdHistoricos` - Historial de propietarios (numero, propietario)
- `GeneralPropietarios` - Propietarios generales (propietario)

### 📊 Tablas de Análisis
- `BogotaRadioBarmanpre` - Datos de radio Barmanpre (grupo_radio)

## 🚀 Configuración Inicial

### 1. Configurar Variables de Entorno

Asegúrate de que tu archivo `.env` contenga las credenciales correctas:

```env
# Aurora MySQL Database
DB_HOST=your-aurora-endpoint.cluster-xxxxxx.us-east-1.rds.amazonaws.com
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=your_database_name
```

### 2. Verificar Estructura

```bash
make verify-structure
```

Este script verificará:
- ✅ Estructura de directorios
- ✅ Archivos de modelos individuales
- ✅ Archivos de configuración

### 3. Probar Conexión

```bash
make test-db
```

### 4. Crear Migración Inicial

```bash
make db-migrate-initial
```

## 📊 Estructura de Modelos

### Modelo Base (`app/models/base.py`)
Todos los modelos heredan de `CustomBase` que incluye:
- `id`: Clave primaria autoincremental
- `created_at`: Fecha de creación
- `updated_at`: Fecha de última actualización
- `to_dict()`: Método para convertir a diccionario
- `__repr__()`: Representación string del modelo

### Campos Reales de la Base de Datos

#### 🏠 **Tablas Barmanpre**
- **Identificadores**: `grupo`, `barmanpre`, `chip`
- **Datos JSON**: `catastro_predios`, `general_catastro`, `POT`, `prediales`, `transacciones_barmanpre`
- **Geográficos**: `latitud`, `longitud`, `geometry`
- **Timestamps**: `fecha_update`

#### 🏘️ **Tablas de Barrios**
- **Identificadores**: `scacodigo`
- **Datos JSON**: `dane`, `valorizacion`, `valoresbarrio`

#### 📍 **Tablas de Códigos**
- **Identificadores**: `code`, `codproyecto`
- **Datos JSON**: `listings`, `output`
- **Geográficos**: `latitud`, `longitud`, `geometry`

#### 🗺️ **Tablas de Lotes**
- **Identificadores**: `grupo`, `barmanpre`, `manzcodigo`
- **Normativa**: `lista`, `pisos`, `altura_min_pot`, `tratamiento`
- **Geográficos**: `latitud`, `longitud`, `geometry`

## 🔧 Uso de los Modelos

### Importar Modelos Individuales

```python
# Importar modelos específicos
from app.models.bogota_models.barmanpre_chip import BogotaBarmanpreChip
from app.models.bogota_models.barmanpre_listings import BogotaBarmanpreListings
from app.models.bogota_models.barrio_dane import BogotaBarrioDane
```

### Importar Todos los Modelos

```python
# Importar desde el módulo principal
from app.models import (
    BogotaBarmanpreChip,
    BogotaBarmanpreListings,
    BogotaBarrioDane,
    # ... otros modelos
)

# O importar desde el módulo de Bogotá
from app.models.bogota_models import (
    BogotaBarmanpreChip,
    BogotaBarmanpreListings,
    BogotaBarrioDane,
    # ... otros modelos
)
```

### Consultas Básicas

```python
from sqlalchemy.orm import Session
from app.core.database import get_db

# Obtener propiedades por grupo
def get_properties_by_group(grupo: int):
    db = next(get_db())
    return db.query(BogotaBarmanpreChip).filter(
        BogotaBarmanpreChip.grupo == grupo
    ).all()

# Obtener transacciones por barmanpre
def get_transactions_by_barmanpre(barmanpre: str):
    db = next(get_db())
    return db.query(BogotaBarmanpreTransacciones).filter(
        BogotaBarmanpreTransacciones.barmanpre == barmanpre
    ).first()

# Obtener barrios por código
def get_neighborhood_by_code(scacodigo: str):
    db = next(get_db())
    return db.query(BogotaBarrioDane).filter(
        BogotaBarrioDane.scacodigo == scacodigo
    ).first()
```

## 📈 Índices Optimizados

Los modelos incluyen índices basados en la estructura real de la base de datos:

- `grupo`: Grupo de propiedades (UNIQUE en varias tablas)
- `barmanpre`: Código Barmanpre (UNIQUE en varias tablas)
- `chip`: Identificación catastral (UNIQUE)
- `scacodigo`: Código de barrio (UNIQUE)
- `code`: Código de propiedad (UNIQUE)
- `geometry`: Campos geométricos (MUL - múltiples índices)

## 🔍 Consultas Avanzadas

### Análisis de Propiedades por Grupo

```python
from sqlalchemy import func

def get_properties_analysis_by_group():
    db = next(get_db())
    return db.query(
        BogotaBarmanpreChip.grupo,
        func.count(BogotaBarmanpreChip.id).label('total_properties'),
        func.avg(BogotaBarmanpreChip.latitud).label('avg_lat'),
        func.avg(BogotaBarmanpreChip.longitud).label('avg_lng')
    ).group_by(
        BogotaBarmanpreChip.grupo
    ).all()
```

### Transacciones por Período

```python
from datetime import datetime

def get_transactions_by_date_range(start_date: datetime, end_date: datetime):
    db = next(get_db())
    return db.query(BogotaBarmanpreTransacciones).filter(
        BogotaBarmanpreTransacciones.fecha_update.between(start_date, end_date)
    ).all()
```

### Propiedades con Geometría

```python
def get_properties_with_geometry():
    db = next(get_db())
    return db.query(BogotaLotesGeometry).filter(
        BogotaLotesGeometry.geometry.isnot(None)
    ).all()
```

## 🛠️ Mantenimiento

### Verificar Estado de Migraciones

```bash
make migrate-status
```

### Crear Nueva Migración

```bash
make migrate-create
```

### Revertir Migración

```bash
alembic downgrade -1
```

## 📝 Ventajas de la Estructura Real

### ✅ **Precisión Total**
- **Columnas exactas**: Cada columna refleja la estructura real de la BD
- **Tipos de datos correctos**: VARCHAR, LONGTEXT, DOUBLE, GEOMETRY, etc.
- **Restricciones apropiadas**: UNIQUE, MUL (índices), NULL/NOT NULL
- **Campos JSON**: LONGTEXT para datos estructurados

### ✅ **Compatibilidad Completa**
- **Datos existentes**: Compatible con todos los datos actuales
- **Consultas optimizadas**: Índices reales para mejor rendimiento
- **Relaciones correctas**: Claves foráneas y relaciones apropiadas
- **Geometría**: Soporte para campos POINT y GEOMETRY

### ✅ **Escalabilidad**
- **Agregar nuevos campos**: Sin afectar la estructura existente
- **Modificar tipos**: Manteniendo compatibilidad
- **Nuevas tablas**: Fácil integración con la estructura actual
- **Migraciones seguras**: Alembic para cambios controlados

### ✅ **Rendimiento Optimizado**
- **Índices reales**: Basados en la estructura actual de la BD
- **Consultas eficientes**: Optimizadas para los patrones de uso reales
- **Tipos de datos apropiados**: Para el tamaño y tipo de datos
- **Geometría nativa**: Soporte para consultas espaciales

## 🆘 Solución de Problemas

### Error de Importación
- Verificar que el archivo `__init__.py` esté actualizado
- Confirmar que el modelo esté exportado en `__all__`
- Revisar la ruta de importación

### Error de Migración
- Verificar que Alembic esté configurado correctamente
- Confirmar que los modelos estén importados en `env.py`
- Revisar logs de Alembic para detalles específicos

### Error de Estructura
- Ejecutar `make verify-structure`
- Verificar que todos los archivos estén en su lugar
- Confirmar que los modelos reflejen la estructura real

### Error de Conexión
- Verificar credenciales en `.env`
- Confirmar que el endpoint de Aurora esté accesible
- Verificar configuración de seguridad (VPC, Security Groups)

## 📞 Soporte

Para problemas específicos con el mapeo de la base de datos, revisa:
1. Logs de la aplicación
2. Documentación de SQLAlchemy
3. Documentación de Alembic
4. Configuración de Aurora MySQL
5. Scripts de verificación incluidos
6. Estructura real de la base de datos 