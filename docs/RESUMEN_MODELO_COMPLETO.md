# Modelo Dimensional Completo - PuntaFina Data Warehouse

## 📊 Resumen Ejecutivo

**Empresa:** PuntaFina - Venta de Calzado  
**Canales:** 5 tiendas físicas + 1 tienda en línea  
**Sistemas:** OroCRM y OroCommerce  
**Años de operación:** 2 años (2023-2025)  

---

## 🎯 Objetivos del Proyecto

### Decisiones Clave a Soportar
- ✅ Ventas diarias, mensuales y anuales
- ✅ Niveles de inventario diario y mensual
- ✅ Productos más vendidos
- ✅ Clientes más importantes
- ✅ Estado de resultados y balance general
- ✅ Costos de inventarios

### KPIs Principales
1. **Costo promedio de inventario mensual**
2. **Cumplimiento de meta de venta mensual**
3. **Margen bruto**
4. **Margen neto**

---

## 🏗️ Arquitectura del Data Warehouse

### Modelo Estrella Completo

```
                    ┌─────────────────────┐
                    │   MÓDULO VENTAS     │
                    └─────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   dim_fecha           dim_cliente          dim_producto
   dim_usuario         dim_sitio_web        dim_canal
   dim_direccion       dim_envio            dim_pago
   dim_impuestos       dim_promocion        dim_orden
   dim_line_item
        │
        └──────────────► fact_ventas ◄──────────────┐
                             │                       │
                    ┌─────────────────────┐         │
                    │  MÓDULO INVENTARIO  │         │
                    └─────────────────────┘         │
                             │                       │
        ┌────────────────────┼────────────────────┐  │
        │                    │                    │  │
   dim_proveedor       dim_almacen      dim_movimiento_tipo
        │                                              │
        └──────────────► fact_inventario              │
                             │                        │
                    ┌─────────────────────┐           │
                    │  MÓDULO FINANZAS    │           │
                    └─────────────────────┘           │
                             │                        │
        ┌────────────────────┼────────────────────┐   │
        │                    │                    │   │
   dim_cuenta_contable  dim_centro_costo  dim_tipo_transaccion
        │                                              │
        ├──────────────► fact_transacciones_contables │
        │                                              │
        ├──────────────► fact_estado_resultados       │
        │                                              │
        └──────────────► fact_balance_general         │
                                                       │
                         Integración ◄─────────────────┘
```

---

## 📋 Inventario de Tablas

### MÓDULO VENTAS (13 dimensiones + 1 fact)

| Tabla | Tipo | Registros (est.) | Descripción |
|-------|------|------------------|-------------|
| `dim_fecha` | Dimensión | ~1,100 | Calendario 2023-2025 🔗 **Compartida con todos los módulos** |
| `dim_cliente` | Dimensión | ~5,000 | Clientes únicos |
| `dim_producto` | Dimensión | ~500 | Catálogo de calzado 🔗 **Compartida con Inventario** |
| `dim_usuario` | Dimensión | ~50 | Usuarios del sistema 🔗 **Compartida con Inventario/Finanzas** |
| `dim_sitio_web` | Dimensión | ~7 | Sitios web (6 tiendas + ecommerce) |
| `dim_canal` | Dimensión | ~10 | Canales de venta |
| `dim_direccion` | Dimensión | ~2,000 | Direcciones de envío |
| `dim_envio` | Dimensión | ~15 | Métodos de envío |
| `dim_pago` | Dimensión | ~5 | Métodos de pago |
| `dim_impuestos` | Dimensión | ~5 | Configuración fiscal |
| `dim_promocion` | Dimensión | ~50 | Promociones y descuentos |
| `dim_orden` | Dimensión | ~10,000 | Órdenes únicas |
| `dim_line_item` | Dimensión | ~30,000 | Líneas de pedido |
| **`fact_ventas`** | **Hecho** | **~30,000** | **Transacciones de venta** |

### MÓDULO INVENTARIO (3 dimensiones propias + 3 compartidas + 1 fact)

**Dimensiones Compartidas con Ventas:**
- 🔗 `dim_producto` - Catálogo de productos
- 🔗 `dim_usuario` - Usuarios del sistema
- 🔗 `dim_fecha` - Calendario

**Dimensiones Propias:**

| Tabla | Tipo | Registros (est.) | Descripción |
|-------|------|------------------|-------------|
| `dim_proveedor` | Dimensión | ~20 | Proveedores de calzado |
| `dim_almacen` | Dimensión | ~7 | Almacenes y tiendas |
| `dim_movimiento_tipo` | Dimensión | 9 | Tipos de movimiento |
| **`fact_inventario`** | **Hecho** | **~100,000** | **Movimientos de inventario** |

### MÓDULO FINANZAS (3 dimensiones propias + 2 compartidas + 3 facts)

**Dimensiones Compartidas:**
- 🔗 `dim_usuario` - Usuarios del sistema
- 🔗 `dim_fecha` - Calendario

**Dimensiones Propias:**

| Tabla | Tipo | Registros (est.) | Descripción |
|-------|------|------------------|-------------|
| `dim_cuenta_contable` | Dimensión | ~40 | Plan de cuentas |
| `dim_centro_costo` | Dimensión | ~9 | Centros de costo |
| `dim_tipo_transaccion` | Dimensión | 9 | Tipos de transacción |
| **`fact_transacciones_contables`** | **Hecho** | **~200,000** | **Asientos contables** |
| **`fact_estado_resultados`** | **Hecho** | **~1,000** | **Estado de resultados mensual** |
| **`fact_balance_general`** | **Hecho** | **~2,000** | **Balance general a fecha** |

**TOTAL:** 19 dimensiones únicas + 5 facts = **24 tablas**

**Nota:** `dim_producto`, `dim_usuario` y `dim_fecha` son **dimensiones conformadas** (compartidas entre módulos), lo que permite análisis integrado cross-module.

---

## 🔗 Integración Entre Módulos

### Ventas ↔ Inventario
```sql
-- Costo de productos vendidos
SELECT 
    fv.id_producto,
    dp.nombre as producto,
    SUM(fv.cantidad) as unidades_vendidas,
    AVG(fi.costo_unitario) as costo_promedio,
    SUM(fv.total_linea_neto) as ingresos_totales,
    SUM(fv.cantidad * fi.costo_unitario) as costo_total,
    SUM(fv.total_linea_neto) - SUM(fv.cantidad * fi.costo_unitario) as utilidad_bruta
FROM fact_ventas fv
JOIN dim_producto dp ON fv.id_producto = dp.id_producto
JOIN fact_inventario fi ON fv.id_producto = fi.id_producto 
    AND fi.id_tipo_movimiento = 'MOV_ENTRADA'
WHERE fv.id_fecha >= 20240101
GROUP BY fv.id_producto, dp.nombre;
```

### Ventas ↔ Finanzas
```sql
-- Registro contable automático desde ventas
INSERT INTO fact_transacciones_contables (...)
SELECT 
    'AST-' || TO_CHAR(fecha_venta, 'YYYY-MM') || '-' || ROW_NUMBER() OVER (...),
    id_fecha,
    '1102' as id_cuenta,  -- Banco
    id_sitio_web as id_centro_costo,
    'TRX_VENTA',
    id_usuario,
    'debe',
    total_orden,
    numero_orden,
    'Registro automático de venta'
FROM fact_ventas;
```

### Inventario ↔ Finanzas
```sql
-- Valorización de inventario
SELECT 
    fi.id_producto,
    dp.nombre,
    SUM(CASE WHEN dmt.categoria = 'entrada' THEN fi.cantidad ELSE 0 END) as entradas,
    SUM(CASE WHEN dmt.categoria = 'salida' THEN fi.cantidad ELSE 0 END) as salidas,
    MAX(fi.stock_resultante) as stock_actual,
    AVG(fi.costo_unitario) as costo_promedio,
    MAX(fi.stock_resultante) * AVG(fi.costo_unitario) as valor_inventario
FROM fact_inventario fi
JOIN dim_producto dp ON fi.id_producto = dp.id_producto
JOIN dim_movimiento_tipo dmt ON fi.id_tipo_movimiento = dmt.id_tipo_movimiento
GROUP BY fi.id_producto, dp.nombre;
```

---

## 📈 Consultas de Negocio Clave

### 1. Ventas Diarias, Mensuales y Anuales
```sql
-- Ventas mensuales con crecimiento
SELECT 
    df.año,
    df.mes,
    df.nombre_mes,
    COUNT(DISTINCT fv.id_order) as ordenes,
    SUM(fv.cantidad) as unidades_vendidas,
    SUM(fv.total_linea_neto) as ventas_netas,
    LAG(SUM(fv.total_linea_neto)) OVER (ORDER BY df.año, df.mes) as ventas_mes_anterior,
    ROUND(((SUM(fv.total_linea_neto) / LAG(SUM(fv.total_linea_neto)) OVER (ORDER BY df.año, df.mes)) - 1) * 100, 2) as crecimiento_pct
FROM fact_ventas fv
JOIN dim_fecha df ON fv.id_fecha = df.id_fecha
GROUP BY df.año, df.mes, df.nombre_mes
ORDER BY df.año, df.mes;
```

### 2. Niveles de Inventario Diario y Mensual
```sql
-- Inventario por día
SELECT 
    df.fecha,
    da.nombre_almacen,
    dp.nombre as producto,
    MAX(fi.stock_resultante) as stock_final,
    AVG(fi.costo_unitario) as costo_promedio,
    MAX(fi.stock_resultante) * AVG(fi.costo_unitario) as valor_inventario
FROM fact_inventario fi
JOIN dim_fecha df ON fi.id_fecha = df.id_fecha
JOIN dim_almacen da ON fi.id_almacen = da.id_almacen
JOIN dim_producto dp ON fi.id_producto = dp.id_producto
WHERE df.fecha >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY df.fecha, da.nombre_almacen, dp.nombre, dp.id_producto
ORDER BY df.fecha DESC, dp.nombre;
```

### 3. Productos Más Vendidos
```sql
-- Top 20 productos más vendidos
SELECT 
    dp.sku,
    dp.nombre,
    SUM(fv.cantidad) as unidades_vendidas,
    COUNT(DISTINCT fv.id_order) as ordenes,
    SUM(fv.total_linea_neto) as ingresos_totales,
    AVG(fv.precio_unitario) as precio_promedio,
    MAX(dp.stock_actual) as stock_actual
FROM fact_ventas fv
JOIN dim_producto dp ON fv.id_producto = dp.id_producto
JOIN dim_fecha df ON fv.id_fecha = df.id_fecha
WHERE df.año = 2024
GROUP BY dp.id_producto, dp.sku, dp.nombre
ORDER BY unidades_vendidas DESC
LIMIT 20;
```

### 4. Clientes Más Importantes
```sql
-- Top clientes por volumen de compras
SELECT 
    dc.nombre as cliente,
    COUNT(DISTINCT fv.id_order) as ordenes,
    SUM(fv.cantidad) as unidades_compradas,
    SUM(fv.total_linea_neto) as compras_totales,
    AVG(fv.total_orden) as ticket_promedio,
    MAX(df.fecha) as ultima_compra,
    CURRENT_DATE - MAX(df.fecha) as dias_sin_comprar
FROM fact_ventas fv
JOIN dim_cliente dc ON fv.id_cliente = dc.id_cliente
JOIN dim_fecha df ON fv.id_fecha = df.id_fecha
GROUP BY dc.id_cliente, dc.nombre
HAVING SUM(fv.total_linea_neto) > 1000
ORDER BY compras_totales DESC
LIMIT 50;
```

### 5. Estado de Resultados
```sql
-- Estado de resultados mensual
WITH cuentas_resultado AS (
    SELECT 
        fer.año,
        fer.mes,
        dcc.nombre_cuenta,
        dcc.tipo_cuenta,
        SUM(fer.saldo_neto) as saldo
    FROM fact_estado_resultados fer
    JOIN dim_cuenta_contable dcc ON fer.id_cuenta = dcc.id_cuenta
    WHERE dcc.estado_financiero = 'resultados'
    GROUP BY fer.año, fer.mes, dcc.nombre_cuenta, dcc.tipo_cuenta
)
SELECT 
    año,
    mes,
    SUM(CASE WHEN tipo_cuenta = 'ingreso' THEN saldo ELSE 0 END) as ingresos,
    SUM(CASE WHEN tipo_cuenta = 'costo' THEN saldo ELSE 0 END) as costos,
    SUM(CASE WHEN tipo_cuenta = 'gasto' THEN saldo ELSE 0 END) as gastos,
    SUM(CASE WHEN tipo_cuenta = 'gasto_financiero' THEN saldo ELSE 0 END) as gastos_financieros,
    SUM(CASE WHEN tipo_cuenta = 'ingreso' THEN saldo ELSE 0 END) -
    SUM(CASE WHEN tipo_cuenta IN ('costo', 'gasto', 'gasto_financiero') THEN saldo ELSE 0 END) as utilidad_neta
FROM cuentas_resultado
GROUP BY año, mes
ORDER BY año DESC, mes DESC;
```

### 6. Balance General
```sql
-- Balance general a fecha
SELECT 
    dcc.tipo_cuenta,
    SUM(fbg.saldo) as total
FROM fact_balance_general fbg
JOIN dim_cuenta_contable dcc ON fbg.id_cuenta = dcc.id_cuenta
WHERE fbg.id_fecha = (SELECT MAX(id_fecha) FROM fact_balance_general)
    AND dcc.nivel = 2  -- Cuentas de segundo nivel
GROUP BY dcc.tipo_cuenta
ORDER BY 
    CASE dcc.tipo_cuenta 
        WHEN 'activo' THEN 1
        WHEN 'pasivo' THEN 2
        WHEN 'patrimonio' THEN 3
    END;
```

### 7. Costo Promedio de Inventario Mensual
```sql
-- KPI: Costo promedio de inventario mensual
WITH inventario_diario AS (
    SELECT 
        df.año,
        df.mes,
        df.fecha,
        SUM(fi.stock_resultante * fi.costo_unitario) as valor_inventario_dia
    FROM fact_inventario fi
    JOIN dim_fecha df ON fi.id_fecha = df.id_fecha
    GROUP BY df.año, df.mes, df.fecha
)
SELECT 
    año,
    mes,
    AVG(valor_inventario_dia) as costo_promedio_inventario_mensual,
    MIN(valor_inventario_dia) as inventario_minimo,
    MAX(valor_inventario_dia) as inventario_maximo
FROM inventario_diario
GROUP BY año, mes
ORDER BY año DESC, mes DESC;
```

### 8. Margen Bruto y Margen Neto
```sql
-- KPI: Márgenes por período
SELECT 
    df.año,
    df.mes,
    SUM(fv.total_linea_neto) as ventas_netas,
    SUM(fv.cantidad * (SELECT AVG(costo_unitario) 
                       FROM fact_inventario fi2 
                       WHERE fi2.id_producto = fv.id_producto)) as costo_ventas,
    SUM(fv.total_linea_neto) - SUM(fv.cantidad * (SELECT AVG(costo_unitario) 
                                                   FROM fact_inventario fi2 
                                                   WHERE fi2.id_producto = fv.id_producto)) as utilidad_bruta,
    ROUND(((SUM(fv.total_linea_neto) - SUM(fv.cantidad * (SELECT AVG(costo_unitario) 
                                                           FROM fact_inventario fi2 
                                                           WHERE fi2.id_producto = fv.id_producto))) 
           / SUM(fv.total_linea_neto)) * 100, 2) as margen_bruto_pct
FROM fact_ventas fv
JOIN dim_fecha df ON fv.id_fecha = df.id_fecha
GROUP BY df.año, df.mes
ORDER BY df.año DESC, df.mes DESC;
```

---

## 📁 Estructura de Archivos del Proyecto

```
PuntaFina_DW_Oro-main/
│
├── config/
│   ├── settings.yaml              # Configuración general
│   └── .env                        # Credenciales (no incluido en repo)
│
├── data/
│   ├── inputs/
│   │   ├── dim_fechas.csv         # Calendario predefinido
│   │   ├── inventario/            # ✨ NUEVO
│   │   │   ├── proveedores.csv
│   │   │   ├── almacenes.csv
│   │   │   ├── tipos_movimiento.csv
│   │   │   └── movimientos_inventario.csv
│   │   └── finanzas/              # ✨ NUEVO
│   │       ├── cuentas_contables.csv
│   │       ├── centros_costo.csv
│   │       ├── tipos_transaccion.csv
│   │       └── transacciones_contables.csv
│   │
│   └── outputs/
│       ├── parquet/                # Archivos optimizados
│       │   ├── dim_*.parquet      # 19 dimensiones
│       │   └── fact_*.parquet     # 5 facts
│       └── csv/                    # Archivos para revisión
│           ├── dim_*.csv
│           └── fact_*.csv
│
├── docs/
│   ├── diccionario_campos.md      # Documentación original
│   ├── ESTRUCTURA_INVENTARIO_FINANZAS.md  # ✨ NUEVO
│   ├── GUIA_USO_INVENTARIO_FINANZAS.md    # ✨ NUEVO
│   └── RESUMEN_MODELO_COMPLETO.md         # ✨ NUEVO (este archivo)
│
├── scripts/
│   ├── build_all_dimensions.py    # Dimensiones de ventas
│   ├── build_fact_ventas.py       # Fact de ventas
│   ├── build_inventario_finanzas.py  # ✨ NUEVO
│   ├── setup_database.py          # ✨ ACTUALIZADO
│   └── orquestador_maestro.py     # ✨ ACTUALIZADO
│
├── Dashboard_PBI/                  # Dashboards de Power BI
│
└── README.md                       # Documentación principal
```

---

## 🚀 Flujo de Ejecución

### Paso 1: Preparar Datos de Entrada
1. Completar archivos CSV en `data/inputs/inventario/`
2. Completar archivos CSV en `data/inputs/finanzas/`

### Paso 2: Ejecutar ETL Completo
```bash
cd scripts
python orquestador_maestro.py
```

Esto ejecuta:
1. `build_all_dimensions.py` → Dimensiones de Ventas
2. `build_fact_ventas.py` → Fact de Ventas
3. **`build_inventario_finanzas.py`** → Dimensiones y Facts de Inventario y Finanzas ✨
4. `setup_database.py` → Crea todas las tablas en PostgreSQL

### Paso 3: Validar Datos
```sql
-- Contar registros por tabla
SELECT 
    schemaname,
    tablename,
    n_live_tup as registros
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY n_live_tup DESC;
```

### Paso 4: Conectar Power BI
- Usar conexión directa a PostgreSQL
- Cargar todas las tablas dim_* y fact_*
- Definir relaciones automáticas

---

## 🎯 Dashboards Recomendados

### Dashboard 1: Ventas
- Ventas diarias/mensuales/anuales
- Top 20 productos más vendidos
- Top clientes
- Ventas por canal
- Ventas por tienda

### Dashboard 2: Inventario
- Stock actual por producto
- Stock actual por almacén
- Movimientos de entrada/salida
- Costo promedio de inventario
- Rotación de inventario
- Alertas de stock mínimo

### Dashboard 3: Finanzas
- Estado de resultados mensual
- Balance general a fecha
- Margen bruto y neto
- Gastos por centro de costo
- Flujo de efectivo

### Dashboard 4: KPIs Ejecutivos
- Cumplimiento de meta de ventas
- Margen bruto %
- Margen neto %
- Costo promedio de inventario
- Días de inventario
- Razón corriente

---

## ✅ Validaciones Implementadas

### Integridad Referencial
- ✅ Todas las foreign keys definidas
- ✅ Validación de existencia de IDs relacionados

### Consistencia de Datos
- ✅ Stock anterior + movimiento = stock resultante
- ✅ Debe = Haber en asientos contables
- ✅ Costo total = cantidad × costo unitario

### Calidad de Datos
- ✅ Campos obligatorios no nulos
- ✅ Tipos de datos validados
- ✅ Valores dentro de rangos esperados

---

## 📞 Contacto y Soporte

**Documentación adicional:**
- [ESTRUCTURA_INVENTARIO_FINANZAS.md](ESTRUCTURA_INVENTARIO_FINANZAS.md)
- [GUIA_USO_INVENTARIO_FINANZAS.md](GUIA_USO_INVENTARIO_FINANZAS.md)
- [diccionario_campos.md](diccionario_campos.md)

**Logs del sistema:**
- `logs/pipeline_YYYYMMDD_HHMMSS.log`

---

**Última actualización:** 16 de Diciembre de 2025  
**Versión:** 2.0 - Incluye módulos de Inventario y Finanzas
