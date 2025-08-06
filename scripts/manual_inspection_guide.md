# Guía para Inspección Manual de la Estructura de la Base de Datos

## 🔍 **Problema Identificado**

Los modelos actuales tienen columnas inferidas que pueden no coincidir con la estructura real de tu base de datos MySQL Aurora AWS.

## 📋 **Pasos para Inspeccionar la Estructura Real**

### 1. **Conectar a la Base de Datos**

Puedes usar cualquier cliente MySQL (MySQL Workbench, DBeaver, phpMyAdmin, etc.) o la línea de comandos:

```bash
mysql -h [TU_HOST] -P [PUERTO] -u [USUARIO] -p [NOMBRE_DB]
```

### 2. **Listar las Tablas de Bogotá**

```sql
SHOW TABLES LIKE '%bogota%';
SHOW TABLES LIKE '%general_propietarios%';
```

### 3. **Inspeccionar la Estructura de Cada Tabla**

Para cada tabla, ejecuta:

```sql
DESCRIBE nombre_tabla;
-- o
SHOW CREATE TABLE nombre_tabla;
```

### 4. **Tablas que Necesitas Inspeccionar**

Basándote en tu lista original, inspecciona estas tablas:

#### 🏠 **Tablas de Propiedades (Barmanpre)**
- `bogota_barmanpre_caracteristicas`
- `bogota_barmanpre_chip`
- `bogota_barmanpre_listings`
- `bogota_barmanpre_POT`
- `bogota_barmanpre_prediales_actuales`
- `bogota_barmanpre_prediales_totales`
- `bogota_barmanpre_proyectos`
- `bogota_barmanpre_transacciones`

#### 🏘️ **Tablas de Barrios y Ubicaciones**
- `bogota_barrio_dane`
- `bogota_barrio_listings`

#### 📍 **Tablas de Códigos y Geometría**
- `bogota_bycode_listings`
- `bogota_bycode_listings_geometry`
- `bogota_bycodigo_proyectos`
- `bogota_chip_transacciones`

#### 🗺️ **Tablas de Lotes y Normativa**
- `bogota_lotes_geometry`
- `bogota_lotes_normativa`
- `bogota_lotes_normativa_dict`
- `bogota_lotes_point`

#### 👥 **Tablas de Propietarios**
- `bogota_propietarios_shd_historicos`
- `general_propietarios`

#### 📊 **Tablas de Análisis**
- `bogota_radio_barmanpre`

## 📝 **Formato de Salida Esperado**

Para cada tabla, necesitas obtener información como esta:

```sql
-- Ejemplo para bogota_barmanpre_chip
DESCRIBE bogota_barmanpre_chip;

+-------------+--------------+------+-----+---------+----------------+
| Field       | Type         | Null | Key | Default | Extra          |
+-------------+--------------+------+-----+---------+----------------+
| id          | int          | NO   | PRI | NULL    | auto_increment |
| chip        | varchar(50)  | NO   | MUL | NULL    |                |
| direccion   | varchar(500) | YES  |     | NULL    |                |
| barrio      | varchar(200) | YES  |     | NULL    |                |
| localidad   | varchar(100) | YES  |     | NULL    |                |
| latitud     | decimal(10,8)| YES  |     | NULL    |                |
| longitud    | decimal(11,8)| YES  |     | NULL    |                |
| created_at  | timestamp    | NO   |     | NULL    |                |
| updated_at  | timestamp    | NO   |     | NULL    |                |
+-------------+--------------+------+-----+---------+----------------+
```

## 🔧 **Script SQL para Obtener Toda la Información**

Puedes ejecutar este script SQL para obtener la estructura de todas las tablas de una vez:

```sql
-- Script para obtener estructura de todas las tablas de Bogotá
SELECT 
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_KEY,
    COLUMN_DEFAULT,
    EXTRA
FROM 
    INFORMATION_SCHEMA.COLUMNS 
WHERE 
    TABLE_SCHEMA = '[TU_NOMBRE_DB]' 
    AND (
        TABLE_NAME LIKE '%bogota%' 
        OR TABLE_NAME = 'general_propietarios'
    )
ORDER BY 
    TABLE_NAME, 
    ORDINAL_POSITION;
```

## 📊 **Mapeo de Tipos de Datos**

Una vez que tengas la estructura real, usa este mapeo para convertir a SQLAlchemy:

| MySQL Type | SQLAlchemy Type | Ejemplo |
|------------|----------------|---------|
| `int` | `Integer` | `Column(Integer, nullable=False)` |
| `bigint` | `BigInteger` | `Column(BigInteger, nullable=False)` |
| `varchar(n)` | `String(n)` | `Column(String(255), nullable=True)` |
| `text` | `Text` | `Column(Text, nullable=True)` |
| `decimal(p,s)` | `Numeric(p,s)` | `Column(Numeric(10,2), nullable=True)` |
| `float` | `Float` | `Column(Float, nullable=True)` |
| `datetime` | `DateTime` | `Column(DateTime, nullable=True)` |
| `date` | `Date` | `Column(Date, nullable=True)` |
| `timestamp` | `DateTime` | `Column(DateTime, nullable=True)` |
| `tinyint(1)` | `Boolean` | `Column(Boolean, nullable=True)` |
| `json` | `JSON` | `Column(JSON, nullable=True)` |

## 🎯 **Próximos Pasos**

1. **Ejecuta la inspección** de todas las tablas usando los comandos SQL anteriores
2. **Guarda la salida** en un archivo para referencia
3. **Compárteme la estructura real** de las tablas
4. **Generaré los modelos correctos** basados en la estructura real

## 📞 **Alternativa: Script de Conexión Directa**

Si prefieres, puedes crear un script simple de Python que solo use `mysql.connector`:

```python
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

connection = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    port=int(os.getenv('DB_PORT', 3306)),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
)

cursor = connection.cursor()

# Listar tablas
cursor.execute("SHOW TABLES LIKE '%bogota%'")
tables = cursor.fetchall()

for table in tables:
    table_name = table[0]
    print(f"\n=== {table_name} ===")
    
    cursor.execute(f"DESCRIBE {table_name}")
    columns = cursor.fetchall()
    
    for column in columns:
        print(f"  {column[0]}: {column[1]} {'(NULL)' if column[2] == 'YES' else '(NOT NULL)'}")

cursor.close()
connection.close()
```

## ✅ **Resultado Esperado**

Una vez que tengas la estructura real, podremos:
1. Generar modelos SQLAlchemy precisos
2. Mapear correctamente los tipos de datos
3. Incluir las restricciones correctas (NULL/NOT NULL, índices, etc.)
4. Crear relaciones apropiadas entre tablas 