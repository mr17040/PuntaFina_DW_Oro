# 📊 Modelo Dimensional CORRECTO de Ventas

## 🎯 fact_ventas - Esquema Estrella Real

```
                    ┌─────────────────┐
                    │   dim_fecha     │
                    │   (4,018)       │
                    │  [CONFORMADA]   │
                    └────────┬────────┘
                             │
                             │ FK: fecha_id
                             │
    ┌─────────────┐          │          ┌──────────────┐
    │ dim_cliente │          │          │ dim_producto │
    │  (20,155)   │          │          │     (64)     │
    └──────┬──────┘          │          └──────┬───────┘
           │                 │                 │
           │ FK: cliente_id  │  FK: producto_id│
           │                 │                 │
    ┌──────┴──────┬──────────┴─────────┬───────┴──────┐
    │             │                    │              │
    │    ┌────────┴─────────┐          │              │
    │    │                  │          │              │
    │    │  FACT_VENTAS     │          │              │
    │    │   (115,528)      │          │              │
    │    │                  │          │              │
    │    │ MEDIDAS:         │          │              │
    │    │ • cantidad       │          │              │
    │    │ • precio_unit    │          │              │
    │    │ • subtotal       │          │              │
    │    │ • descuento      │          │              │
    │    │ • impuesto  ⚠️   │          │              │
    │    │ • envio          │          │              │
    │    │ • total          │          │              │
    │    │ • costo_unit     │          │              │
    │    │ • costo_total    │          │              │
    │    │ • margen         │          │              │
    │    │                  │          │              │
    │    └────┬────┬────┬───┘          │              │
    │         │    │    │              │              │
    └─────────┘    │    └──────────────┘              │
                   │                                  │
    FK: orden_id   │ FK: usuario_id   FK: almacen_id │
                   │                                  │
    ┌──────────────┴┐  ┌──────────────┐  ┌──────────┴───┐
    │  dim_orden    │  │ dim_usuario  │  │ dim_almacen  │
    │   (42,119)    │  │    (54)      │  │     (6)      │
    │               │  │ [CONFORMADA] │  │  [TIENDAS]   │
    └───────────────┘  └──────────────┘  └──────────────┘


    ⚠️ NOTA: impuesto es NUMERIC (monto), NO hay FK a dim_impuestos
```

## ✅ 6 Foreign Keys Confirmados

| FK en fact_ventas | Apunta a | Registros | Propósito |
|-------------------|----------|-----------|-----------|
| `fecha_id` | dim_fecha | 4,018 | Cuándo se vendió |
| `cliente_id` | dim_cliente | 20,155 | Quién compró |
| `producto_id` | **dim_producto** | **64** | **Qué se vendió** ⭐ |
| `orden_id` | dim_orden | 42,119 | En qué orden |
| `usuario_id` | dim_usuario | 54 | Quién procesó la venta |
| `almacen_id` | dim_almacen | 6 | De qué tienda salió 🏪 |

---

## ❌ Dimensiones NO Conectadas a fact_ventas

Estas tablas existen pero NO tienen FK desde fact_ventas:

| Dimensión | Registros | Estado | Razón |
|-----------|-----------|--------|-------|
| dim_sitio_web | 5 | Catálogo | No vinculada directamente |
| dim_canal | 2 | Catálogo | No vinculada directamente |
| dim_direccion | 79,836 | Catálogo | Relacionada a cliente/orden |
| dim_envio | 8 | Catálogo | Relacionada a orden |
| dim_pago | 10 | Catálogo | Relacionada a orden |
| dim_estado_orden | 16 | Catálogo | Relacionada a orden |
| dim_estado_pago | 6 | Catálogo | Relacionada a pago |
| dim_promocion | 2 | Catálogo | Posible FK futuro |
| dim_line_item | 5,000 | Lookup | Catálogo de tipos de línea |
| **dim_impuestos** | 5 | ⚠️ | **Existe pero no usada** |
| **dim_detalle_venta** | 1 | ⚠️ | **Solo registro dummy** |

---

## 🔧 Relaciones Indirectas (a través de dim_orden)

Algunas dimensiones están relacionadas con `dim_orden`, no directamente con `fact_ventas`:

```
fact_ventas.orden_id → dim_orden
                          ↓
        ┌─────────────────┴──────────────────┐
        ↓                 ↓                   ↓
   dim_canal      dim_sitio_web       dim_direccion
   dim_envio      dim_estado_orden    dim_pago
```

**Para acceder:**
```sql
-- Ejemplo: Ventas por canal
SELECT 
    c.nombre as canal,
    SUM(v.total) as total_ventas
FROM fact_ventas v
JOIN dim_orden o ON v.orden_id = o.orden_id
JOIN dim_canal c ON o.canal_externo_id = c.canal_externo_id  -- Relación indirecta
GROUP BY c.canal_id, c.nombre;
```

---

## ⚠️ CONFUSIONES ACLARADAS

### 1. dim_producto vs dim_detalle_venta

| Tabla | Registros | Uso Real |
|-------|-----------|----------|
| **dim_producto** | 64 | ✅ **ESTA ES LA CORRECTA** |
| dim_detalle_venta | 1 | ❌ Solo dummy "Sin detalle" |

**fact_ventas usa `producto_id` que apunta a dim_producto**

### 2. dim_almacen - ¿Para qué sirve?

🏪 **Identifica de qué tienda/almacén salió el producto vendido**

**6 almacenes/tiendas:**
```sql
SELECT * FROM dim_almacen;
-- Ej: Tienda Centro, Tienda Norte, Almacén Online, etc.
```

**Caso de uso:**
```sql
-- Ranking de tiendas por ventas
SELECT 
    a.nombre,
    COUNT(*) as num_ventas,
    SUM(v.total) as ingresos
FROM fact_ventas v
JOIN dim_almacen a ON v.almacen_id = a.almacen_id
GROUP BY a.almacen_id, a.nombre
ORDER BY ingresos DESC;
```

### 3. dim_impuestos - ¿Por qué no está conectada?

⚠️ **Diseño actual: impuesto como MONTO, no como referencia**

```sql
-- En fact_ventas
impuesto NUMERIC(10,2)  -- Monto: $1.30, $5.60, etc.

-- NO existe
impuesto_id INTEGER FK  -- ❌ No existe este campo
```

**dim_impuestos existe (5 registros) pero no se usa en el modelo actual**

### 4. dim_orden y dim_line_item - ¿Son "Atributos Degenerados"?

❌ **NO. Esa clasificación es incorrecta:**

| Tabla | Clasificación Correcta | Registros | FK desde fact_ventas |
|-------|------------------------|-----------|----------------------|
| dim_orden | **Dimensión Real** | 42,119 | ✅ SÍ (orden_id) |
| dim_line_item | **Lookup Table** | 5,000 | ❌ NO |

**dim_orden es una dimensión completa con FK, NO un atributo degenerado**

---

## 📋 Resumen Visual

```
┌─────────────────────────────────────────────────────────┐
│                    FACT_VENTAS                          │
│                                                         │
│  ✅ 6 Dimensiones Conectadas por FK:                   │
│     1. dim_fecha (4,018)                               │
│     2. dim_cliente (20,155)                            │
│     3. dim_producto (64) ⭐ LA CORRECTA                │
│     4. dim_orden (42,119)                              │
│     5. dim_usuario (54)                                │
│     6. dim_almacen (6) 🏪                              │
│                                                         │
│  ⚠️ Dimensiones NO Conectadas:                         │
│     - dim_impuestos (5) - existe pero no usada        │
│     - dim_detalle_venta (1) - solo dummy              │
│     - 9 dimensiones de catálogo más                   │
│                                                         │
│  📊 115,528 registros                                  │
└─────────────────────────────────────────────────────────┘
```

---

**Generado:** 2026-01-05  
**Fuente:** Verificación directa en base de datos PostgreSQL
