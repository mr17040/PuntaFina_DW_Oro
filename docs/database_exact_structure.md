# 📋 Documentación Exacta de la Base de Datos

**Base de datos:** datawarehouse_bi
**Total de tablas:** 29

## 📊 Resumen

- **Dimensiones:** 24
- **Tablas de Hechos:** 5

## 🔷 Dimensiones


### 📊 dim_almacen

**Registros:** 6

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| almacen_id | INTEGER | PK | No | AUTO | |
| codigo | VARCHAR(50) | - | Sí | - | |
| nombre | VARCHAR(255) | - | Sí | - | |
| direccion | VARCHAR(255) | - | Sí | - | |
| ciudad | VARCHAR(100) | - | Sí | - | |
| pais | VARCHAR(100) | - | Sí | - | |
| capacidad | INTEGER | - | Sí | - | |
| tipo | VARCHAR(50) | - | Sí | - | |
| activo | BOOLEAN | - | Sí | true | |

**Índices:**
- `dim_almacen_codigo_key`
- `dim_almacen_pkey`
- `idx_dim_almacen_codigo`

---

### 📊 dim_canal

**Registros:** 2

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| canal_id | INTEGER | PK | No | AUTO | |
| canal_externo_id | INTEGER | - | Sí | - | |
| codigo | VARCHAR(50) | - | Sí | - | |
| nombre | VARCHAR(255) | - | Sí | - | |
| tipo | VARCHAR(50) | - | Sí | - | |
| activo | BOOLEAN | - | Sí | true | |

**Índices:**
- `dim_canal_pkey`

---

### 📊 dim_categoria_producto

**Registros:** 10

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| categoria_id | INTEGER | PK | No | AUTO | |
| categoria_externo_id | INTEGER | - | Sí | - | |
| codigo | VARCHAR(50) | - | Sí | - | |
| nombre | VARCHAR(255) | - | Sí | - | |
| descripcion | TEXT | - | Sí | - | |
| categoria_padre_id | INTEGER | - | Sí | - | |
| nivel | INTEGER | - | Sí | - | |
| activo | BOOLEAN | - | Sí | true | |

**Índices:**
- `dim_categoria_producto_pkey`

---

### 📊 dim_centro_costo

**Registros:** 9

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| centro_costo_id | INTEGER | PK | No | AUTO | |
| codigo | VARCHAR(50) | - | Sí | - | |
| nombre | VARCHAR(255) | - | Sí | - | |
| descripcion | TEXT | - | Sí | - | |
| tipo | VARCHAR(50) | - | Sí | - | |
| responsable | VARCHAR(255) | - | Sí | - | |
| activo | BOOLEAN | - | Sí | true | |

**Índices:**
- `dim_centro_costo_codigo_key`
- `dim_centro_costo_pkey`
- `idx_dim_centro_codigo`

---

### 📊 dim_cliente

**Registros:** 20,155

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| cliente_id | INTEGER | PK | No | AUTO | |
| cliente_externo_id | INTEGER | - | Sí | - | |
| codigo_cliente | VARCHAR(50) | - | Sí | - | |
| nombre | VARCHAR(255) | - | Sí | - | |
| tipo_cliente | VARCHAR(50) | - | Sí | - | |
| segmento | VARCHAR(50) | - | Sí | - | |
| email | VARCHAR(255) | - | Sí | - | |
| telefono | VARCHAR(50) | - | Sí | - | |
| activo | BOOLEAN | - | Sí | true | |
| fecha_registro | TIMESTAMP | - | Sí | - | |
| created_at | TIMESTAMP | - | Sí | NOW | |

**Índices:**
- `dim_cliente_pkey`
- `idx_dim_cliente_externo`

---

### 📊 dim_cuenta_contable

**Registros:** 42

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| cuenta_id | INTEGER | PK | No | AUTO | |
| codigo | VARCHAR(50) | - | Sí | - | |
| nombre | VARCHAR(255) | - | Sí | - | |
| descripcion | TEXT | - | Sí | - | |
| tipo | VARCHAR(50) | - | Sí | - | |
| categoria | VARCHAR(50) | - | Sí | - | |
| nivel | INTEGER | - | Sí | - | |
| cuenta_padre | VARCHAR(50) | - | Sí | - | |
| activo | BOOLEAN | - | Sí | true | |

**Índices:**
- `dim_cuenta_contable_codigo_key`
- `dim_cuenta_contable_pkey`
- `idx_dim_cuenta_codigo`

---

### 📊 dim_detalle_venta

**Registros:** 1

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| detalle_id | INTEGER | PK | No | AUTO | |
| codigo | VARCHAR(50) | - | Sí | - | |
| descripcion | TEXT | - | Sí | - | |
| created_at | TIMESTAMP | - | Sí | NOW | |

**Índices:**
- `dim_detalle_venta_pkey`

---

### 📊 dim_direccion

**Registros:** 79,836

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| direccion_id | INTEGER | PK | No | AUTO | |
| direccion_externo_id | INTEGER | - | Sí | - | |
| calle | VARCHAR(255) | - | Sí | - | |
| ciudad | VARCHAR(100) | - | Sí | - | |
| estado | VARCHAR(100) | - | Sí | - | |
| codigo_postal | VARCHAR(20) | - | Sí | - | |
| pais | VARCHAR(100) | - | Sí | - | |
| tipo_direccion | VARCHAR(50) | - | Sí | - | |

**Índices:**
- `dim_direccion_pkey`

---

### 📊 dim_envio

**Registros:** 8

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| envio_id | INTEGER | PK | No | AUTO | |
| envio_externo_id | INTEGER | - | Sí | - | |
| metodo_envio | VARCHAR(100) | - | Sí | - | |
| transportista | VARCHAR(100) | - | Sí | - | |
| costo_envio | NUMERIC(10,2) | - | Sí | - | |
| tiempo_estimado_dias | INTEGER | - | Sí | - | |

**Índices:**
- `dim_envio_pkey`

---

### 📊 dim_estado_orden

**Registros:** 16

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| estado_orden_id | INTEGER | PK | No | AUTO | |
| codigo | VARCHAR(50) | - | Sí | - | |
| nombre | VARCHAR(100) | - | Sí | - | |
| descripcion | TEXT | - | Sí | - | |
| activo | BOOLEAN | - | Sí | true | |

**Índices:**
- `dim_estado_orden_codigo_key`
- `dim_estado_orden_pkey`

---

### 📊 dim_estado_pago

**Registros:** 6

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| estado_pago_id | INTEGER | PK | No | AUTO | |
| codigo | VARCHAR(50) | - | Sí | - | |
| nombre | VARCHAR(100) | - | Sí | - | |
| descripcion | TEXT | - | Sí | - | |
| activo | BOOLEAN | - | Sí | true | |

**Índices:**
- `dim_estado_pago_codigo_key`
- `dim_estado_pago_pkey`

---

### 📊 dim_fecha

**Registros:** 4,018

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| fecha_id | INTEGER | PK | No | AUTO | |
| fecha | DATE | - | No | - | |
| anio | INTEGER | - | No | - | |
| mes | INTEGER | - | No | - | |
| dia | INTEGER | - | No | - | |
| trimestre | INTEGER | - | No | - | |
| semana_anio | INTEGER | - | No | - | |
| dia_semana | INTEGER | - | No | - | |
| dia_semana_nombre | VARCHAR(20) | - | Sí | - | |
| mes_nombre | VARCHAR(20) | - | Sí | - | |
| es_fin_semana | BOOLEAN | - | Sí | false | |
| es_festivo | BOOLEAN | - | Sí | false | |
| nombre_festivo | VARCHAR(100) | - | Sí | - | |
| created_at | TIMESTAMP | - | Sí | NOW | |

**Índices:**
- `dim_fecha_fecha_key`
- `dim_fecha_pkey`
- `idx_dim_fecha_anio_mes`
- `idx_dim_fecha_fecha`

---

### 📊 dim_impuestos

**Registros:** 5

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| impuesto_id | INTEGER | PK | No | AUTO | |
| codigo | VARCHAR(50) | - | Sí | - | |
| nombre | VARCHAR(100) | - | Sí | - | |
| tasa | NUMERIC(5,2) | - | Sí | - | |
| tipo | VARCHAR(50) | - | Sí | - | |

**Índices:**
- `dim_impuestos_pkey`

---

### 📊 dim_line_item

**Registros:** 5,000

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| line_item_id | INTEGER | PK | No | AUTO | |
| line_item_externo_id | INTEGER | - | Sí | - | |
| numero_linea | INTEGER | - | Sí | - | |
| tipo_linea | VARCHAR(50) | - | Sí | - | |

**Índices:**
- `dim_line_item_pkey`

---

### 📊 dim_orden

**Registros:** 42,119

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| orden_id | INTEGER | PK | No | AUTO | |
| orden_externo_id | INTEGER | - | Sí | - | |
| numero_orden | VARCHAR(100) | - | Sí | - | |
| tipo_orden | VARCHAR(50) | - | Sí | - | |
| canal | VARCHAR(50) | - | Sí | - | |
| moneda | VARCHAR(3) | - | Sí | - | |
| tasa_cambio | NUMERIC(10,4) | - | Sí | 1 | |
| created_at | TIMESTAMP | - | Sí | NOW | |

**Índices:**
- `dim_orden_numero_orden_key`
- `dim_orden_pkey`
- `idx_dim_orden_externo`

---

### 📊 dim_pago

**Registros:** 10

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| pago_id | INTEGER | PK | No | AUTO | |
| pago_externo_id | INTEGER | - | Sí | - | |
| metodo_pago | VARCHAR(100) | - | Sí | - | |
| procesador | VARCHAR(100) | - | Sí | - | |
| tipo_pago | VARCHAR(50) | - | Sí | - | |

**Índices:**
- `dim_pago_pkey`

---

### 📊 dim_periodo_contable

**Registros:** 84

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| periodo_id | INTEGER | PK | No | AUTO | |
| anio | INTEGER | - | No | - | |
| mes | INTEGER | - | No | - | |
| trimestre | INTEGER | - | No | - | |
| nombre_periodo | VARCHAR(50) | - | Sí | - | |
| fecha_inicio | DATE | - | Sí | - | |
| fecha_fin | DATE | - | Sí | - | |
| cerrado | BOOLEAN | - | Sí | false | |

**Índices:**
- `dim_periodo_contable_anio_mes_key`
- `dim_periodo_contable_pkey`

---

### 📊 dim_producto

**Registros:** 64

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| producto_id | INTEGER | PK | No | AUTO | |
| producto_externo_id | INTEGER | - | Sí | - | |
| sku | VARCHAR(100) | - | Sí | - | |
| nombre | VARCHAR(500) | - | Sí | - | |
| descripcion | TEXT | - | Sí | - | |
| categoria | VARCHAR(100) | - | Sí | - | |
| marca | VARCHAR(100) | - | Sí | - | |
| tipo | VARCHAR(50) | - | Sí | - | |
| unidad_medida | VARCHAR(20) | - | Sí | - | |
| precio_base | NUMERIC(10,2) | - | Sí | - | |
| costo_estandar | NUMERIC(10,2) | - | Sí | - | |
| activo | BOOLEAN | - | Sí | true | |
| created_at | TIMESTAMP | - | Sí | NOW | |

**Índices:**
- `dim_producto_pkey`
- `dim_producto_sku_key`
- `idx_dim_producto_externo`
- `idx_dim_producto_sku`

---

### 📊 dim_promocion

**Registros:** 2

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| promocion_id | INTEGER | PK | No | AUTO | |
| promocion_externo_id | INTEGER | - | Sí | - | |
| codigo | VARCHAR(50) | - | Sí | - | |
| nombre | VARCHAR(255) | - | Sí | - | |
| descripcion | TEXT | - | Sí | - | |
| tipo_descuento | VARCHAR(50) | - | Sí | - | |
| valor_descuento | NUMERIC(10,2) | - | Sí | - | |
| fecha_inicio | DATE | - | Sí | - | |
| fecha_fin | DATE | - | Sí | - | |

**Índices:**
- `dim_promocion_pkey`

---

### 📊 dim_proveedor

**Registros:** 8

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| proveedor_id | INTEGER | PK | No | AUTO | |
| codigo | VARCHAR(50) | - | Sí | - | |
| nombre | VARCHAR(255) | - | Sí | - | |
| contacto | VARCHAR(255) | - | Sí | - | |
| email | VARCHAR(255) | - | Sí | - | |
| telefono | VARCHAR(50) | - | Sí | - | |
| direccion | VARCHAR(255) | - | Sí | - | |
| ciudad | VARCHAR(100) | - | Sí | - | |
| pais | VARCHAR(100) | - | Sí | - | |
| activo | BOOLEAN | - | Sí | true | |

**Índices:**
- `dim_proveedor_codigo_key`
- `dim_proveedor_pkey`
- `idx_dim_proveedor_codigo`

---

### 📊 dim_sitio_web

**Registros:** 5

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| sitio_id | INTEGER | PK | No | AUTO | |
| sitio_externo_id | INTEGER | - | Sí | - | |
| codigo | VARCHAR(50) | - | Sí | - | |
| nombre | VARCHAR(255) | - | Sí | - | |
| url | VARCHAR(500) | - | Sí | - | |
| pais | VARCHAR(100) | - | Sí | - | |
| idioma | VARCHAR(10) | - | Sí | - | |
| moneda_default | VARCHAR(3) | - | Sí | - | |
| activo | BOOLEAN | - | Sí | true | |

**Índices:**
- `dim_sitio_web_pkey`

---

### 📊 dim_tipo_movimiento

**Registros:** 9

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| tipo_movimiento_id | INTEGER | PK | No | AUTO | |
| codigo | VARCHAR(50) | - | Sí | - | |
| nombre | VARCHAR(100) | - | Sí | - | |
| descripcion | TEXT | - | Sí | - | |
| tipo | VARCHAR(50) | - | Sí | - | |
| afecta_stock | VARCHAR(20) | - | Sí | - | |
| activo | BOOLEAN | - | Sí | true | |

**Índices:**
- `dim_tipo_movimiento_codigo_key`
- `dim_tipo_movimiento_pkey`
- `idx_dim_tipo_mov_codigo`

---

### 📊 dim_tipo_transaccion

**Registros:** 9

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| tipo_transaccion_id | INTEGER | PK | No | AUTO | |
| codigo | VARCHAR(50) | - | Sí | - | |
| nombre | VARCHAR(100) | - | Sí | - | |
| descripcion | TEXT | - | Sí | - | |
| categoria | VARCHAR(50) | - | Sí | - | |
| afecta_flujo | VARCHAR(20) | - | Sí | - | |
| activo | BOOLEAN | - | Sí | true | |

**Índices:**
- `dim_tipo_transaccion_codigo_key`
- `dim_tipo_transaccion_pkey`
- `idx_dim_tipo_trans_codigo`

---

### 📊 dim_usuario

**Registros:** 54

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| usuario_id | INTEGER | PK | No | AUTO | |
| usuario_externo_id | INTEGER | - | Sí | - | |
| username | VARCHAR(255) | - | Sí | - | |
| email | VARCHAR(255) | - | Sí | - | |
| nombre_completo | VARCHAR(255) | - | Sí | - | |
| activo | BOOLEAN | - | Sí | true | |
| created_at | TIMESTAMP | - | Sí | NOW | |
| updated_at | TIMESTAMP | - | Sí | NOW | |

**Índices:**
- `dim_usuario_pkey`
- `idx_dim_usuario_externo`

---
## 🎯 Tablas de Hechos (Facts)


### 📊 fact_balance

**Registros:** 210

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| balance_id | INTEGER | PK | No | AUTO | |
| periodo_id | INTEGER | FK | Sí | - | |
| cuenta_id | INTEGER | FK | Sí | - | |
| saldo_inicial | NUMERIC(15,2) | - | Sí | - | |
| debitos | NUMERIC(15,2) | - | Sí | - | |
| creditos | NUMERIC(15,2) | - | Sí | - | |
| saldo_final | NUMERIC(15,2) | - | Sí | - | |
| created_at | TIMESTAMP | - | Sí | NOW | |

**Foreign Keys:**
- `periodo_id` → `dim_periodo_contable(periodo_id)`
- `cuenta_id` → `dim_cuenta_contable(cuenta_id)`

**Índices:**
- `fact_balance_periodo_id_cuenta_id_key`
- `fact_balance_pkey`
- `idx_fact_balance_cuenta`
- `idx_fact_balance_periodo`

---

### 📊 fact_estado_resultados

**Registros:** 70

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| resultado_id | INTEGER | PK | No | AUTO | |
| periodo_id | INTEGER | FK | Sí | - | |
| cuenta_id | INTEGER | FK | Sí | - | |
| centro_costo_id | INTEGER | FK | Sí | - | |
| ingresos | NUMERIC(15,2) | - | Sí | - | |
| costos | NUMERIC(15,2) | - | Sí | - | |
| gastos | NUMERIC(15,2) | - | Sí | - | |
| utilidad_bruta | NUMERIC(15,2) | - | Sí | - | |
| utilidad_neta | NUMERIC(15,2) | - | Sí | - | |
| created_at | TIMESTAMP | - | Sí | NOW | |

**Foreign Keys:**
- `periodo_id` → `dim_periodo_contable(periodo_id)`
- `cuenta_id` → `dim_cuenta_contable(cuenta_id)`
- `centro_costo_id` → `dim_centro_costo(centro_costo_id)`

**Índices:**
- `fact_estado_resultados_pkey`
- `idx_fact_resultado_cuenta`
- `idx_fact_resultado_periodo`

---

### 📊 fact_inventario

**Registros:** 408,397

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| movimiento_id | INTEGER | PK | No | AUTO | |
| fecha_id | INTEGER | FK | Sí | - | |
| producto_id | INTEGER | FK | Sí | - | |
| almacen_id | INTEGER | FK | Sí | - | |
| tipo_movimiento_id | INTEGER | FK | Sí | - | |
| proveedor_id | INTEGER | FK | Sí | - | |
| usuario_id | INTEGER | FK | Sí | - | |
| cantidad | NUMERIC(10,2) | - | Sí | - | |
| costo_unitario | NUMERIC(10,2) | - | Sí | - | |
| costo_total | NUMERIC(10,2) | - | Sí | - | |
| stock_anterior | NUMERIC(10,2) | - | Sí | - | |
| stock_resultante | NUMERIC(10,2) | - | Sí | - | |
| documento | VARCHAR(100) | - | Sí | - | |
| observaciones | TEXT | - | Sí | - | |
| created_at | TIMESTAMP | - | Sí | NOW | |

**Foreign Keys:**
- `fecha_id` → `dim_fecha(fecha_id)`
- `producto_id` → `dim_producto(producto_id)`
- `almacen_id` → `dim_almacen(almacen_id)`
- `tipo_movimiento_id` → `dim_tipo_movimiento(tipo_movimiento_id)`
- `proveedor_id` → `dim_proveedor(proveedor_id)`
- `usuario_id` → `dim_usuario(usuario_id)`

**Índices:**
- `fact_inventario_pkey`
- `idx_fact_inv_almacen`
- `idx_fact_inv_fecha`
- `idx_fact_inv_producto`

---

### 📊 fact_transacciones

**Registros:** 577,640

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| transaccion_id | INTEGER | PK | No | AUTO | |
| fecha_id | INTEGER | FK | Sí | - | |
| cuenta_id | INTEGER | FK | Sí | - | |
| centro_costo_id | INTEGER | FK | Sí | - | |
| tipo_transaccion_id | INTEGER | FK | Sí | - | |
| usuario_id | INTEGER | FK | Sí | - | |
| numero_asiento | VARCHAR(50) | - | Sí | - | |
| tipo_movimiento | VARCHAR(10) | - | Sí | - | |
| monto | NUMERIC(15,2) | - | Sí | - | |
| documento_referencia | VARCHAR(100) | - | Sí | - | |
| descripcion | TEXT | - | Sí | - | |
| orden_id | INTEGER | - | Sí | - | |
| movimiento_inventario_id | INTEGER | - | Sí | - | |
| created_at | TIMESTAMP | - | Sí | NOW | |
| periodo_id | INTEGER | FK | Sí | - | |

**Foreign Keys:**
- `fecha_id` → `dim_fecha(fecha_id)`
- `cuenta_id` → `dim_cuenta_contable(cuenta_id)`
- `centro_costo_id` → `dim_centro_costo(centro_costo_id)`
- `tipo_transaccion_id` → `dim_tipo_transaccion(tipo_transaccion_id)`
- `usuario_id` → `dim_usuario(usuario_id)`
- `periodo_id` → `dim_periodo_contable(periodo_id)`

**Índices:**
- `fact_transacciones_pkey`
- `idx_fact_trans_centro`
- `idx_fact_trans_cuenta`
- `idx_fact_trans_fecha`
- `idx_fact_trans_periodo`

---

### 📊 fact_ventas

**Registros:** 115,528

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| venta_id | INTEGER | PK | No | AUTO | |
| fecha_id | INTEGER | FK | Sí | - | |
| cliente_id | INTEGER | FK | Sí | - | |
| producto_id | INTEGER | FK | Sí | - | |
| orden_id | INTEGER | FK | Sí | - | |
| usuario_id | INTEGER | FK | Sí | - | |
| almacen_id | INTEGER | FK | Sí | - | |
| cantidad | NUMERIC(10,2) | - | Sí | - | |
| precio_unitario | NUMERIC(10,2) | - | Sí | - | |
| subtotal | NUMERIC(10,2) | - | Sí | - | |
| descuento | NUMERIC(10,2) | - | Sí | - | |
| impuesto | NUMERIC(10,2) | - | Sí | - | |
| envio | NUMERIC(10,2) | - | Sí | - | |
| total | NUMERIC(10,2) | - | Sí | - | |
| costo_unitario | NUMERIC(10,2) | - | Sí | - | |
| costo_total | NUMERIC(10,2) | - | Sí | - | |
| margen | NUMERIC(10,2) | - | Sí | - | |
| created_at | TIMESTAMP | - | Sí | NOW | |

**Foreign Keys:**
- `fecha_id` → `dim_fecha(fecha_id)`
- `cliente_id` → `dim_cliente(cliente_id)`
- `producto_id` → `dim_producto(producto_id)`
- `orden_id` → `dim_orden(orden_id)`
- `usuario_id` → `dim_usuario(usuario_id)`
- `almacen_id` → `dim_almacen(almacen_id)`

**Índices:**
- `fact_ventas_pkey`
- `idx_fact_ventas_cliente`
- `idx_fact_ventas_fecha`
- `idx_fact_ventas_producto`

---
