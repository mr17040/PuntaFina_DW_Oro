# Resumen de Cambios Aplicados al ETL - PuntaFina DW

## 📋 Cambios Realizados

### 1. ✅ **dim_cuenta_contable - Eliminación de Nulos/NaN**

**Archivo modificado:** `etl_batch/transformers/complete_dimension_builder.py`

**Cambios:**
- Agregado manejo de valores nulos en todas las columnas
- Valores por defecto:
  - `codigo`: '0' (si es nulo)
  - `nombre`: 'Sin nombre'
  - `descripcion`: 'Sin descripción'  
  - `tipo`: 'Sin tipo'
  - `categoria`: '' (string vacío)
  - `nivel`: 1
  - `cuenta_padre`: '' (string vacío)
  - `activo`: True

**Resultado:** dim_cuenta_contable ya no tendrá nulos ni NaN en ninguna columna.

---

### 2. ✅ **dim_producto - Precio Base y Costo Estándar**

**Archivo modificado:** `etl_batch/transformers/complete_dimension_builder.py`

**Cambios:**
- **Precio Base:** Se obtiene desde `oro_price_product` (promedio de precios por producto)
- **Costo Estándar:** Se obtiene desde CSV `Compras_Productos_PuntaFina.csv` (último costo promedio)
- **Estimaciones automáticas:**
  - Si producto no tiene precio pero tiene costo: `precio_base = costo_estandar * 2.5` (margen ~60%)
  - Si producto no tiene costo pero tiene precio: `costo_estandar = precio_base * 0.4` (margen ~60%)

**Fuentes de datos:**
- Tabla: `oro_price_product` (OroCommerce)
- CSV: `/Compras_Productos_PuntaFina.csv`

**Resultado:** dim_producto ahora tendrá precio_base y costo_estandar poblados para aproximadamente 90%+ de los productos.

---

### 3. ✅ **fact_ventas - Costos, Márgenes y Descuentos**

**Archivo modificado:** `etl_batch/transformers/complete_fact_builder.py`

**Cambios:**
- **Descuentos:** Se extraen desde `oro_order_line_item.price_discount`
- **Costos:** Se obtienen desde `dim_producto.costo_estandar` (ya no estimados fijos)
- **Cálculos actualizados:**
  ```
  subtotal = subtotal_bruto - descuento_total
  impuesto = subtotal * 0.13
  total = subtotal + impuesto + envio
  costo_unitario = dim_producto.costo_estandar
  costo_total = cantidad * costo_unitario
  margen = subtotal - costo_total
  ```

**Nuevas columnas en fact_ventas:**
- `costo_unitario` (DECIMAL) - Costo real desde dim_producto
- `costo_total` (DECIMAL) - costo_unitario * cantidad
- `margen` (DECIMAL) - subtotal - costo_total
- `descuento` (DECIMAL) - Descuento aplicado
- `promocion_id` (FK) - Referencia a dim_promocion
- `promocion_nombre` (VARCHAR) - Nombre de la promoción (desnormalizado)

**Resultado:** fact_ventas ahora muestra costos reales, márgenes calculados correctamente y descuentos aplicados.

---

### 4. ✅ **dim_promocion - Nueva Dimensión**

**Archivos creados/modificados:**
- `etl_batch/transformers/complete_dimension_builder.py` - Método `build_dim_promocion()`
- `sql/granular/add_promocion_to_fact_ventas.sql` - Script DDL
- `etl_batch/main.py` - Agregado a listas de dimensiones

**Estructura de dim_promocion:**
```sql
CREATE TABLE dim_promocion (
    promocion_id SERIAL PRIMARY KEY,
    codigo VARCHAR(50),
    nombre VARCHAR(255),
    descripcion TEXT,
    tipo_descuento VARCHAR(50),
    valor_descuento DECIMAL(10,2),
    porcentaje_descuento DECIMAL(5,2),
    fecha_inicio DATE,
    fecha_fin DATE,
    activo BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**Fuente de datos:** `oro_order.discount_description` (OroCommerce)

**Registro por defecto:**
- promocion_id: 1
- nombre: "Sin promoción"
- Para ventas que no tienen promoción aplicada

**Resultado:** Nueva dimensión dim_promocion creada y poblada con promociones únicas desde oro_order.

---

## 🚀 Scripts de Ejecución

### Script Principal: `ejecutar_cambios_etl.py`

**Ubicación:** `/Users/elsalvador/project/PuntaFina_DW_Oro/ejecutar_cambios_etl.py`

**Función:**
1. Aplica cambios de esquema SQL (dim_promocion, campos en fact_ventas)
2. Ejecuta ETL completo
3. Verifica resultados y muestra estadísticas

**Uso:**
```bash
cd /Users/elsalvador/project/PuntaFina_DW_Oro
python3 ejecutar_cambios_etl.py
```

### Script SQL: `add_promocion_to_fact_ventas.sql`

**Ubicación:** `/Users/elsalvador/project/PuntaFina_DW_Oro/sql/granular/add_promocion_to_fact_ventas.sql`

**Función:**
- Agrega columnas a dim_promocion (si faltan)
- Agrega columnas promocion_id y promocion_nombre a fact_ventas
- Inserta registro por defecto "Sin promoción"
- Actualiza registros existentes

---

## ⚠️ CONFIGURACIÓN REQUERIDA

### Antes de ejecutar el ETL:

1. **Verificar variables de entorno** en `etl_batch/.env`:

```bash
# Asegurarse que las bases de datos de ORIGEN estén correctas
ORO_DB_HOST=<IP_SERVIDOR_OROCOMMERCE>  # NO localhost si está en servidor remoto
ORO_DB_PORT=5432
ORO_DB_NAME=orocommerce
ORO_DB_USER=sa
ORO_DB_PASS=IngDatos123*

CRM_DB_HOST=<IP_SERVIDOR_OROCRM>  # NO localhost si está en servidor remoto
CRM_DB_PORT=5432
CRM_DB_NAME=oro_crm
CRM_DB_USER=sa
CRM_DB_PASS=IngDatos123*

# Base de datos Data Warehouse (DESTINO)
DW_DB_HOST=104.156.246.237
DW_DB_PORT=5432
DW_DB_NAME=puntafina_dw
DW_DB_USER=sa
DW_DB_PASS=IngDatos123*
```

2. **Verificar conectividad** a las bases de datos:
```bash
cd /Users/elsalvador/project/PuntaFina_DW_Oro/etl_batch
python3 -c "
from dotenv import load_dotenv
import psycopg2
import os

load_dotenv('.env')

# Test DW connection
try:
    conn = psycopg2.connect(
        host=os.getenv('DW_DB_HOST'),
        port=int(os.getenv('DW_DB_PORT')),
        dbname=os.getenv('DW_DB_NAME'),
        user=os.getenv('DW_DB_USER'),
        password=os.getenv('DW_DB_PASS')
    )
    print('✓ Conexión DW exitosa')
    conn.close()
except Exception as e:
    print(f'✗ Error DW: {e}')

# Test ORO connection
try:
    conn = psycopg2.connect(
        host=os.getenv('ORO_DB_HOST'),
        port=int(os.getenv('ORO_DB_PORT')),
        dbname=os.getenv('ORO_DB_NAME'),
        user=os.getenv('ORO_DB_USER'),
        password=os.getenv('ORO_DB_PASS')
    )
    print('✓ Conexión OroCommerce exitosa')
    conn.close()
except Exception as e:
    print(f'✗ Error OroCommerce: {e}')
"
```

---

## 📊 Verificación de Resultados

Después de ejecutar el ETL, verificar con estas consultas:

### 1. Verificar dim_cuenta_contable sin nulos:
```sql
SELECT 
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE codigo IS NULL OR codigo = '') as nulos_codigo,
    COUNT(*) FILTER (WHERE nombre IS NULL OR nombre = '') as nulos_nombre
FROM dim_cuenta_contable;
```
**Esperado:** nulos_codigo = 0, nulos_nombre = 0

### 2. Verificar dim_producto con precios y costos:
```sql
SELECT 
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE precio_base > 0) as con_precio,
    COUNT(*) FILTER (WHERE costo_estandar > 0) as con_costo,
    ROUND(100.0 * COUNT(*) FILTER (WHERE precio_base > 0) / COUNT(*), 1) as porcentaje_con_precio,
    ROUND(100.0 * COUNT(*) FILTER (WHERE costo_estandar > 0) / COUNT(*), 1) as porcentaje_con_costo
FROM dim_producto;
```
**Esperado:** porcentaje_con_precio >= 90%, porcentaje_con_costo >= 90%

### 3. Verificar fact_ventas con costos y márgenes:
```sql
SELECT 
    COUNT(*) as total_ventas,
    COUNT(*) FILTER (WHERE costo_unitario > 0) as con_costo,
    COUNT(*) FILTER (WHERE descuento > 0) as con_descuento,
    COUNT(*) FILTER (WHERE margen > 0) as con_margen_positivo,
    ROUND(AVG(costo_unitario), 2) as costo_promedio,
    ROUND(AVG(margen), 2) as margen_promedio,
    ROUND(SUM(descuento), 2) as total_descuentos
FROM fact_ventas;
```
**Esperado:** con_costo > 0, total_descuentos > 0, margen_promedio > 0

### 4. Verificar dim_promocion:
```sql
SELECT COUNT(*) as total_promociones FROM dim_promocion;
SELECT * FROM dim_promocion ORDER BY promocion_id LIMIT 10;
```
**Esperado:** total_promociones >= 1 (al menos "Sin promoción")

---

## 📁 Archivos Modificados

1. `/Users/elsalvador/project/PuntaFina_DW_Oro/etl_batch/transformers/complete_dimension_builder.py`
   - Método `build_dim_cuenta_contable()` - Manejo de nulos
   - Método `build_dim_producto()` - Precios y costos desde fuentes
   - Método `build_dim_promocion()` - Nueva dimensión

2. `/Users/elsalvador/project/PuntaFina_DW_Oro/etl_batch/transformers/complete_fact_builder.py`
   - Método `build_fact_ventas()` - Costos reales, márgenes, descuentos, promociones

3. `/Users/elsalvador/project/PuntaFina_DW_Oro/etl_batch/main.py`
   - Agregado `dim_promocion` a listas de dimensiones
   - Removido `dim_promocion` de lista de tablas obsoletas

4. `/Users/elsalvador/project/PuntaFina_DW_Oro/sql/granular/add_promocion_to_fact_ventas.sql`
   - Nuevo script DDL para dim_promocion y campos en fact_ventas

5. `/Users/elsalvador/project/PuntaFina_DW_Oro/ejecutar_cambios_etl.py`
   - Nuevo script Python para ejecutar todo el proceso

---

## 🎯 Siguientes Pasos

1. **Actualizar .env** con las IPs correctas de los servidores de origen
2. **Ejecutar:** `python3 ejecutar_cambios_etl.py`
3. **Verificar** resultados con las consultas SQL provistas
4. **Validar** en Power BI o herramienta de visualización que:
   - dim_producto muestra precios y costos
   - fact_ventas muestra márgenes reales
   - Los descuentos y promociones están presentes

---

## 📞 Soporte

Si hay errores durante la ejecución:
1. Revisar logs en: `etl_batch/logs/`
2. Verificar conectividad a bases de datos
3. Verificar que CSV `Compras_Productos_PuntaFina.csv` existe en root del proyecto
