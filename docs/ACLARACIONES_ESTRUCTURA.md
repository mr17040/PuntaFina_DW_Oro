# 🔍 Aclaraciones Sobre la Estructura del Data Warehouse

**Fecha:** 2026-01-05  
**Basado en:** Análisis directo de la base de datos PostgreSQL

---

## ❓ Preguntas Frecuentes Respondidas

### 1. ¿Dónde está dim_producto?

**✅ RESPUESTA:** dim_producto SÍ existe y ES la dimensión real de productos.

```sql
-- Verificación
SELECT COUNT(*) FROM dim_producto;
-- Resultado: 64 productos

-- fact_ventas usa producto_id como FK
SELECT producto_id FROM fact_ventas LIMIT 1;
-- ✅ FK confirmado: producto_id → dim_producto(producto_id)
```

**⚠️ CONFUSIÓN:** 
- `dim_detalle_venta` existe pero solo tiene 1 registro dummy: "Sin detalle"
- `dim_detalle_venta` NO se usa realmente en el modelo
- La documentación anterior mencionaba "dim_detalle_venta" como sinónimo de productos, pero es incorrecto

**✅ CORRECCIÓN:**
- **dim_producto** = Dimensión REAL de productos (64 productos)
- **dim_detalle_venta** = Tabla residual sin uso práctico (1 registro)

---

### 2. ¿Para qué sirve dim_almacen en ventas?

**✅ RESPUESTA:** dim_almacen identifica de qué almacén/tienda salió el producto vendido.

```sql
-- Confirmación del FK
SELECT almacen_id FROM fact_ventas LIMIT 5;
-- ✅ FK confirmado: almacen_id → dim_almacen(almacen_id)

-- Almacenes disponibles
SELECT almacen_id, codigo, nombre FROM dim_almacen;
```

**📊 Datos:**
- Total: **6 almacenes/tiendas**
- Uso en ventas: Identifica el punto de venta (tienda física o almacén online)

**🎯 Casos de Uso:**
- Analizar ventas por tienda
- Comparar performance entre sucursales
- Rastrear inventario por ubicación
- Análisis geográfico de ventas

**Ejemplo de consulta:**
```sql
SELECT 
    a.nombre as tienda,
    COUNT(*) as total_ventas,
    SUM(v.total) as ingresos_totales
FROM fact_ventas v
JOIN dim_almacen a ON v.almacen_id = a.almacen_id
GROUP BY a.almacen_id, a.nombre
ORDER BY ingresos_totales DESC;
```

---

### 3. ¿Por qué dim_impuestos no está vinculado a ventas?

**⚠️ RESPUESTA:** dim_impuestos existe pero NO está conectada a fact_ventas por FK.

```sql
-- Verificar columnas de impuestos en fact_ventas
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'fact_ventas' AND column_name LIKE '%impuesto%';

-- Resultado:
-- impuesto | numeric (MONTO, no FK)
```

**❌ NO EXISTE:**
- `impuesto_id` (columna FK)
- Relación FK entre fact_ventas y dim_impuestos

**✅ LO QUE SÍ EXISTE:**
- Campo `impuesto` tipo NUMERIC(10,2) - Almacena el MONTO del impuesto
- `dim_impuestos` (5 registros) - Tabla de catálogo no utilizada

**🔧 DISEÑO ACTUAL:**
El sistema almacena directamente el monto del impuesto calculado, no una referencia a la tabla de impuestos.

**💡 IMPLICACIONES:**
- ✅ Más rápido: No requiere JOIN adicional
- ✅ Histórico: Preserva el monto exacto cobrado
- ❌ Menos flexible: No se puede recalcular retroactivamente
- ❌ Sin trazabilidad: No se sabe qué tasa/tipo de impuesto se aplicó

**📝 SI QUISIERAS VINCULAR dim_impuestos:**
Necesitarías:
1. Agregar columna `impuesto_id INTEGER` a fact_ventas
2. Crear FK: `ALTER TABLE fact_ventas ADD CONSTRAINT fk_impuesto FOREIGN KEY (impuesto_id) REFERENCES dim_impuestos(impuesto_id);`
3. Migrar datos existentes

---

### 4. ¿Qué significa "Atributo Degenerado" en dim_orden y dim_line_item?

**🔍 ANÁLISIS DE LA IMAGEN:**

La imagen muestra:
```
12 | dim_orden     | ~1K  | Info descriptiva de órdenes (lookup table)    | oro_order          | Atributo Degenerado
13 | dim_line_item | ~5K  | Info descriptiva de line items (lookup table) | oro_order_line_item| Atributo Degenerado
```

**⚠️ ESTO ES CONFUSO E INCORRECTO:**

**✅ REALIDAD EN LA BASE DE DATOS:**

```sql
-- dim_orden
SELECT COUNT(*) FROM dim_orden;
-- Resultado: 42,119 órdenes (NO ~1K)

-- dim_line_item  
SELECT COUNT(*) FROM dim_line_item;
-- Resultado: 5,000 líneas (correcto)

-- Verificar FK
SELECT orden_id FROM fact_ventas LIMIT 1;
-- ✅ FK existe: orden_id → dim_orden(orden_id)
```

**📚 DEFINICIONES:**

1. **Atributo Degenerado (concepto teórico):**
   - Es un atributo de una transacción (como número de orden)
   - Que NO tiene una dimensión propia
   - Se almacena directamente en la fact table
   - Ejemplo: `numero_factura` VARCHAR en fact_ventas

2. **Lookup Table (tabla de consulta):**
   - Tabla auxiliar con información descriptiva
   - Puede tener o no FK desde fact tables
   - Ejemplo: catálogos, listas de valores

3. **Dimensión Real:**
   - Tabla conectada por FK desde fact table
   - Forma parte del modelo dimensional (estrella)
   - Ejemplo: dim_producto, dim_cliente

**🎯 CLASIFICACIÓN CORRECTA:**

| Tabla | Tipo Real | Registros | FK desde fact_ventas |
|-------|-----------|-----------|----------------------|
| **dim_orden** | Dimensión Real | 42,119 | ✅ SÍ (orden_id) |
| **dim_line_item** | Lookup Table | 5,000 | ❌ NO |
| **dim_producto** | Dimensión Real | 64 | ✅ SÍ (producto_id) |
| **dim_detalle_venta** | Tabla Residual | 1 | ❌ NO (dummy) |

**💡 CONCLUSIÓN:**
- **dim_orden** NO es un "atributo degenerado", es una dimensión REAL con 42K registros
- **dim_line_item** es una lookup table de catálogo (5K tipos de líneas de pedido)
- La imagen tiene información desactualizada o conceptualmente incorrecta

---

## ✅ Tabla de Dimensiones de VENTAS - CORREGIDA

### Dimensiones con FK Directo en fact_ventas (6):

| # | Dimensión | Registros | Propósito |
|---|-----------|-----------|-----------|
| 1 | **dim_fecha** | 4,018 | Dimensión temporal (conformada) |
| 2 | **dim_cliente** | 20,155 | Cliente que compra |
| 3 | **dim_producto** | 64 | ⭐ Producto vendido |
| 4 | **dim_orden** | 42,119 | Información de la orden completa |
| 5 | **dim_usuario** | 54 | Usuario que procesó la venta |
| 6 | **dim_almacen** | 6 | 🏪 Tienda/almacén origen |

### Dimensiones de Catálogo (sin FK directo):

| # | Dimensión | Registros | Estado |
|---|-----------|-----------|---------|
| 7 | dim_sitio_web | 5 | Catálogo |
| 8 | dim_canal | 2 | Catálogo |
| 9 | dim_direccion | 79,836 | Catálogo |
| 10 | dim_envio | 8 | Catálogo |
| 11 | dim_pago | 10 | Catálogo |
| 12 | dim_estado_orden | 16 | Catálogo |
| 13 | dim_estado_pago | 6 | Catálogo |
| 14 | dim_promocion | 2 | Catálogo |
| 15 | dim_line_item | 5,000 | Lookup table |
| 16 | dim_impuestos | 5 | ⚠️ Existe pero no conectada |
| 17 | dim_detalle_venta | 1 | ⚠️ Dummy, no usada |

---

## 🎯 Recomendaciones

### Inmediatas:
1. ✅ Usar **dim_producto** como dimensión de productos (no dim_detalle_venta)
2. ✅ Mantener **dim_almacen** para análisis por tienda
3. ⚠️ Considerar eliminar `dim_detalle_venta` (solo 1 registro dummy)

### Mejoras Futuras:
1. 🔧 Vincular `dim_impuestos` a `fact_ventas` agregando `impuesto_id` FK
2. 🔧 Conectar dimensiones de catálogo (canal, sitio_web, envio) a fact_ventas
3. 📊 Documentar claramente cuáles son dimensiones reales vs lookup tables

---

**Actualizado:** 2026-01-05  
**Verificado contra:** Base de datos datawarehouse_bi en producción
