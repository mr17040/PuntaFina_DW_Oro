# 📋 Catálogo de Estados - Módulo de Ventas

## 🎯 Descripción General

Este documento describe los diferentes estados utilizados en el sistema de ventas de PuntaFina, incluyendo estados de órdenes, pagos y envíos.

---

## 📦 1. Estados de Envío (dim_envio)

### Ubicación del CSV
`data/inputs/ventas/metodos_envio.csv`

### Estructura

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `id_envio` | TEXT | ID único del método de envío | ENV001 |
| `metodo_envio` | TEXT | Nombre del método | Envío Estándar |
| `tiempo_entrega` | TEXT | Tiempo estimado | 5-7 días hábiles |
| `costo` | NUMERIC | Costo del envío | 5.99 |
| `estado` | TEXT | Estado del servicio | activo/suspendido |
| `descripcion` | TEXT | Descripción detallada | Envío regular a domicilio |

### Estados Disponibles

| ID | Método | Tiempo | Costo | Estado |
|----|--------|--------|-------|--------|
| ENV001 | Envío Estándar | 5-7 días hábiles | $5.99 | activo |
| ENV002 | Envío Express | 2-3 días hábiles | $12.99 | activo |
| ENV003 | Envío Premium | 24-48 horas | $24.99 | activo |
| ENV004 | Recogida en Tienda | Inmediato | $0.00 | activo |
| ENV005 | Envío Gratis | 7-10 días hábiles | $0.00 | activo |
| ENV006 | Envío Internacional | 15-20 días hábiles | $35.00 | activo |
| ENV007 | Envío Nocturno | 12 horas | $45.00 | suspendido |
| ENV008 | Courier Especializado | 1-2 días hábiles | $18.50 | activo |

### Valores Válidos para `estado`
- ✅ **activo** - Método disponible para usar
- ⏸️ **suspendido** - Temporalmente no disponible
- ❌ **inactivo** - Descontinuado permanentemente

---

## 💳 2. Estados de Pago (dim_pago)

### Ubicación del CSV
`data/inputs/ventas/estados_pago.csv`

### Estructura

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `id_pago` | TEXT | ID único del estado de pago | PAG001 |
| `metodo_pago` | TEXT | Método de pago | Tarjeta de Crédito |
| `estado_pago` | TEXT | Estado del pago | pending/paid_in_full |
| `descripcion` | TEXT | Descripción del estado | Pago en proceso |
| `requiere_validacion` | BOOLEAN | Si necesita validación | TRUE/FALSE |
| `plazo_dias` | INTEGER | Días para procesar | 0-30 |

### Estados de Pago Disponibles

#### 🔵 Estados en Proceso

| Estado | Descripción | Requiere Validación | Puede Cambiar |
|--------|-------------|---------------------|---------------|
| **pending** | Pago pendiente de confirmación | ✅ Sí | ✅ Sí |
| **authorized** | Autorizado pero no capturado | ✅ Sí | ✅ Sí |
| **processing** | En proceso de validación | ✅ Sí | ✅ Sí |

#### 🟢 Estados Exitosos

| Estado | Descripción | Es Final | Permite Devolución |
|--------|-------------|----------|-------------------|
| **paid_in_full** | Pagado completamente | ✅ Sí | ✅ Sí |
| **partially_paid** | Pago parcial realizado | ❌ No | ✅ Sí |

#### 🔴 Estados de Rechazo

| Estado | Descripción | Es Final | Requiere Acción |
|--------|-------------|----------|----------------|
| **canceled** | Cancelado por cliente/tienda | ✅ Sí | ❌ No |
| **failed** | Pago rechazado | ✅ Sí | ✅ Sí (reintentar) |
| **declined** | Declinado por banco | ✅ Sí | ✅ Sí (otro método) |

### Métodos de Pago

| Método | Estados Comunes | Plazo Validación |
|--------|----------------|------------------|
| Tarjeta de Crédito | pending → authorized → paid_in_full | Inmediato |
| Tarjeta de Débito | pending → paid_in_full | Inmediato |
| Efectivo | paid_in_full | 0 días |
| Transferencia Bancaria | pending → paid_in_full | 1-2 días |
| PayPal | authorized → paid_in_full | Inmediato |
| Crédito Tienda | partially_paid → paid_in_full | 30 días |
| Contra Entrega | pending → paid_in_full | Al entregar |
| Cheque | pending → paid_in_full | 3-5 días |

---

## 📋 3. Estados de Orden (dim_estado_orden)

### Ubicación del CSV
`data/inputs/ventas/estados_orden.csv`

### Estructura

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `id_estado_orden` | TEXT | ID único del estado | EST001 |
| `codigo_estado` | TEXT | Código interno | open |
| `nombre_estado` | TEXT | Nombre legible | Abierta |
| `descripcion` | TEXT | Descripción detallada | Orden creada |
| `orden_flujo` | INTEGER | Secuencia en el flujo | 1-16 |
| `es_estado_final` | BOOLEAN | Si es estado terminal | TRUE/FALSE |
| `permite_modificacion` | BOOLEAN | Si permite edición | TRUE/FALSE |

### Flujo de Estados de Orden

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUJO NORMAL DE ORDEN                        │
└─────────────────────────────────────────────────────────────────┘

1. open (Abierta)
   ↓
2. pending_payment (Pago Pendiente)
   ↓
3. payment_received (Pago Recibido)
   ↓
4. processing (En Procesamiento)
   ↓
5. ready_to_ship (Lista para Envío)
   ↓
6. shipped (Enviada)
   ↓
7. in_transit (En Tránsito)
   ↓
8. out_for_delivery (En Reparto)
   ↓
9. delivered (Entregada) ✅ ESTADO FINAL
   ↓
10. completed (Completada) ✅ ESTADO FINAL
```

### Estados Alternativos

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUJOS ALTERNATIVOS                          │
└─────────────────────────────────────────────────────────────────┘

❌ CANCELACIONES:
11. canceled_by_customer (Cancelada por Cliente) ✅ FINAL
12. canceled_by_store (Cancelada por Tienda) ✅ FINAL

⏸️ PAUSAS:
13. on_hold (En Espera) - Puede reactivarse

❌ ERRORES:
14. failed (Fallida) ✅ FINAL

🔄 DEVOLUCIONES:
15. returned (Devuelta) ✅ FINAL

📦 ENVÍOS PARCIALES:
16. partially_shipped (Enviada Parcial)
```

### Catálogo Completo de Estados

| ID | Código | Nombre | Flujo | Final | Modif |
|----|--------|--------|-------|-------|-------|
| EST001 | open | Abierta | 1 | ❌ | ✅ |
| EST002 | pending_payment | Pago Pendiente | 2 | ❌ | ✅ |
| EST003 | payment_received | Pago Recibido | 3 | ❌ | ❌ |
| EST004 | processing | En Procesamiento | 4 | ❌ | ❌ |
| EST005 | ready_to_ship | Lista para Envío | 5 | ❌ | ❌ |
| EST006 | shipped | Enviada | 6 | ❌ | ❌ |
| EST007 | in_transit | En Tránsito | 7 | ❌ | ❌ |
| EST008 | out_for_delivery | En Reparto | 8 | ❌ | ❌ |
| EST009 | delivered | Entregada | 9 | ✅ | ❌ |
| EST010 | completed | Completada | 10 | ✅ | ❌ |
| EST011 | canceled_by_customer | Cancelada Cliente | 11 | ✅ | ❌ |
| EST012 | canceled_by_store | Cancelada Tienda | 12 | ✅ | ❌ |
| EST013 | on_hold | En Espera | 13 | ❌ | ✅ |
| EST014 | failed | Fallida | 14 | ✅ | ❌ |
| EST015 | returned | Devuelta | 15 | ✅ | ❌ |
| EST016 | partially_shipped | Enviada Parcial | 16 | ❌ | ❌ |

---

## 🔄 Relaciones entre Estados

### Ventas Exitosas
```sql
SELECT 
    eo.nombre_estado as estado_orden,
    dp.estado_pago,
    de.estado as estado_envio,
    COUNT(*) as cantidad_ventas
FROM fact_ventas fv
JOIN dim_estado_orden eo ON fv.id_estado_orden = eo.id_estado_orden
JOIN dim_pago dp ON fv.id_pago = dp.id_pago
JOIN dim_envio de ON fv.id_envio = de.id_envio
WHERE eo.codigo_estado = 'completed'
  AND dp.estado_pago = 'paid_in_full'
GROUP BY eo.nombre_estado, dp.estado_pago, de.estado
ORDER BY cantidad_ventas DESC;
```

### Órdenes Problemáticas
```sql
-- Órdenes canceladas o fallidas
SELECT 
    eo.nombre_estado,
    eo.descripcion,
    COUNT(*) as total,
    SUM(fv.total_linea_neto) as monto_perdido
FROM fact_ventas fv
JOIN dim_estado_orden eo ON fv.id_estado_orden = eo.id_estado_orden
WHERE eo.es_estado_final = TRUE
  AND eo.codigo_estado IN ('canceled_by_customer', 'canceled_by_store', 'failed')
GROUP BY eo.id_estado_orden, eo.nombre_estado, eo.descripcion
ORDER BY monto_perdido DESC;
```

### Análisis de Conversión
```sql
-- Tasa de conversión por estado de pago
SELECT 
    dp.metodo_pago,
    dp.estado_pago,
    COUNT(*) as intentos,
    SUM(CASE WHEN dp.estado_pago = 'paid_in_full' THEN 1 ELSE 0 END) as exitosos,
    ROUND(
        SUM(CASE WHEN dp.estado_pago = 'paid_in_full' THEN 1 ELSE 0 END)::numeric / 
        COUNT(*)::numeric * 100, 
        2
    ) as tasa_conversion_pct
FROM fact_ventas fv
JOIN dim_pago dp ON fv.id_pago = dp.id_pago
GROUP BY dp.metodo_pago, dp.estado_pago
ORDER BY tasa_conversion_pct DESC;
```

---

## 📊 KPIs por Estados

### Métricas de Envío
- **Tasa de entregas exitosas**: delivered / (delivered + failed + returned)
- **Tiempo promedio de entrega**: días entre shipped y delivered
- **Costo promedio de envío por método**

### Métricas de Pago
- **Tasa de aprobación**: paid_in_full / total intentos
- **Tiempo de validación promedio**: por método de pago
- **Tasa de cancelación**: canceled / total

### Métricas de Orden
- **Tasa de completitud**: completed / total órdenes
- **Tasa de cancelación**: (canceled_by_customer + canceled_by_store) / total
- **Órdenes en proceso**: COUNT(WHERE es_estado_final = FALSE)

---

## 🚀 Uso en el ETL

### Carga de Dimensiones
```bash
# El ETL carga automáticamente estos CSVs:
python scripts/build_all_dimensions.py

# Dimensiones creadas:
# - dim_envio (desde data/inputs/ventas/metodos_envio.csv)
# - dim_pago (desde data/inputs/ventas/estados_pago.csv)
# - dim_estado_orden (desde data/inputs/ventas/estados_orden.csv)
```

### Validaciones Automáticas
El ETL valida:
- ✅ Columnas requeridas presentes
- ✅ IDs únicos sin duplicados
- ✅ Estados válidos
- ✅ Valores numéricos correctos

---

## ⚠️ Notas Importantes

1. **NO modificar** los archivos CSV predefinidos sin validar primero
2. Los **estados** son valores maestros que se usan en múltiples tablas
3. Agregar nuevos estados requiere actualizar la documentación
4. Los **códigos de estado** deben ser únicos y descriptivos
5. Mantener consistencia entre estados en diferentes dimensiones

---

**Fecha de creación:** 16 de Diciembre de 2025  
**Versión:** 1.0 - Catálogo Inicial de Estados
