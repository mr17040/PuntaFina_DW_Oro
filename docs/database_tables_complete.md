# 📋 Estructura Completa de Tablas

**Generado:** 2026-01-05 00:51:29

### 📊 dim_almacen
**Registros:** 6

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| almacen_id | INTEGER | PK | No | SERIAL | |
| codigo | VARCHAR(50) | - | Sí | - | |
| nombre | VARCHAR(255) | - | Sí | - | |
| direccion | VARCHAR(255) | - | Sí | - | |
| ciudad | VARCHAR(100) | - | Sí | - | |
| pais | VARCHAR(100) | - | Sí | - | |
| capacidad | INTEGER | - | Sí | - | |
| tipo | VARCHAR(50) | - | Sí | - | |
| activo | BOOLEAN | - | Sí | true | |

---

### 📊 dim_canal
**Registros:** 2

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| canal_id | INTEGER | PK | No | SERIAL | |
| canal_externo_id | INTEGER | - | Sí | - | |
| codigo | VARCHAR(50) | - | Sí | - | |
| nombre | VARCHAR(255) | - | Sí | - | |
| tipo | VARCHAR(50) | - | Sí | - | |
| activo | BOOLEAN | - | Sí | true | |

---

### 📊 dim_categoria_producto
**Registros:** 10

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| categoria_id | INTEGER | PK | No | SERIAL | |
| categoria_externo_id | INTEGER | - | Sí | - | |
| codigo | VARCHAR(50) | - | Sí | - | |
| nombre | VARCHAR(255) | - | Sí | - | |
| descripcion | TEXT | - | Sí | - | |
| categoria_padre_id | INTEGER | - | Sí | - | |
| nivel | INTEGER | - | Sí | - | |
| activo | BOOLEAN | - | Sí | true | |

---

### 📊 dim_centro_costo
**Registros:** 9

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| centro_costo_id | INTEGER | PK | No | SERIAL | |
| codigo | VARCHAR(50) | - | Sí | - | |
| nombre | VARCHAR(255) | - | Sí | - | |
| descripcion | TEXT | - | Sí | - | |
| tipo | VARCHAR(50) | - | Sí | - | |
| responsable | VARCHAR(255) | - | Sí | - | |
| activo | BOOLEAN | - | Sí | true | |

---

### 📊 dim_cliente
**Registros:** 20,155

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| cliente_id | INTEGER | PK | No | SERIAL | |
| cliente_externo_id | INTEGER | - | Sí | - | |
| codigo_cliente | VARCHAR(50) | - | Sí | - | |
| nombre | VARCHAR(255) | - | Sí | - | |
| tipo_cliente | VARCHAR(50) | - | Sí | - | |
| segmento | VARCHAR(50) | - | Sí | - | |
| email | VARCHAR(255) | - | Sí | - | |
| telefono | VARCHAR(50) | - | Sí | - | |
| activo | BOOLEAN | - | Sí | true | |
| fecha_registro | TIMESTAMP | - | Sí | - | |
| created_at | TIMESTAMP | - | Sí | NOW() | |

---

### 📊 dim_cuenta_contable
**Registros:** 42

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| cuenta_id | INTEGER | PK | No | SERIAL | |
| codigo | VARCHAR(50) | - | Sí | - | |
| nombre | VARCHAR(255) | - | Sí | - | |
| descripcion | TEXT | - | Sí | - | |
| tipo | VARCHAR(50) | - | Sí | - | |
| categoria | VARCHAR(50) | - | Sí | - | |
| nivel | INTEGER | - | Sí | - | |
| cuenta_padre | VARCHAR(50) | - | Sí | - | |
| activo | BOOLEAN | - | Sí | true | |

---

### 📊 dim_detalle_venta
**Registros:** 1

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| detalle_id | INTEGER | PK | No | SERIAL | |
| codigo | VARCHAR(50) | - | Sí | - | |
| descripcion | TEXT | - | Sí | - | |
| created_at | TIMESTAMP | - | Sí | NOW() | |

---

### 📊 dim_direccion
**Registros:** 79,836

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| direccion_id | INTEGER | PK | No | SERIAL | |
| direccion_externo_id | INTEGER | - | Sí | - | |
| calle | VARCHAR(255) | - | Sí | - | |
| ciudad | VARCHAR(100) | - | Sí | - | |
| estado | VARCHAR(100) | - | Sí | - | |
| codigo_postal | VARCHAR(20) | - | Sí | - | |
| pais | VARCHAR(100) | - | Sí | - | |
| tipo_direccion | VARCHAR(50) | - | Sí | - | |

---

### 📊 dim_envio
**Registros:** 8

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| envio_id | INTEGER | PK | No | SERIAL | |
| envio_externo_id | INTEGER | - | Sí | - | |
| metodo_envio | VARCHAR(100) | - | Sí | - | |
| transportista | VARCHAR(100) | - | Sí | - | |
| costo_envio | NUMERIC(10,2) | - | Sí | - | |
| tiempo_estimado_dias | INTEGER | - | Sí | - | |

---

### 📊 dim_estado_orden
**Registros:** 16

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| estado_orden_id | INTEGER | PK | No | SERIAL | |
| codigo | VARCHAR(50) | - | Sí | - | |
| nombre | VARCHAR(100) | - | Sí | - | |
| descripcion | TEXT | - | Sí | - | |
| activo | BOOLEAN | - | Sí | true | |

---

### 📊 dim_estado_pago
**Registros:** 6

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| estado_pago_id | INTEGER | PK | No | SERIAL | |
| codigo | VARCHAR(50) | - | Sí | - | |
| nombre | VARCHAR(100) | - | Sí | - | |
| descripcion | TEXT | - | Sí | - | |
| activo | BOOLEAN | - | Sí | true | |

---

### 📊 dim_fecha
**Registros:** 4,018

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| fecha_id | INTEGER | PK | No | SERIAL | |
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
| created_at | TIMESTAMP | - | Sí | NOW() | |

---

### 📊 dim_impuestos
**Registros:** 5

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| impuesto_id | INTEGER | PK | No | SERIAL | |
| codigo | VARCHAR(50) | - | Sí | - | |
| nombre | VARCHAR(100) | - | Sí | - | |
| tasa | NUMERIC(5,2) | - | Sí | - | |
| tipo | VARCHAR(50) | - | Sí | - | |

---

### 📊 dim_line_item
**Registros:** 5,000

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| line_item_id | INTEGER | PK | No | SERIAL | |
| line_item_externo_id | INTEGER | - | Sí | - | |
| numero_linea | INTEGER | - | Sí | - | |
| tipo_linea | VARCHAR(50) | - | Sí | - | |

---

### 📊 dim_orden
**Registros:** 42,119

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| orden_id | INTEGER | PK | No | SERIAL | |
| orden_externo_id | INTEGER | - | Sí | - | |
| numero_orden | VARCHAR(100) | - | Sí | - | |
| tipo_orden | VARCHAR(50) | - | Sí | - | |
| canal | VARCHAR(50) | - | Sí | - | |
| moneda | VARCHAR(3) | - | Sí | - | |
| tasa_cambio | NUMERIC(10,4) | - | Sí | 1 | |
| created_at | TIMESTAMP | - | Sí | NOW() | |

---

### 📊 dim_pago
**Registros:** 10

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| pago_id | INTEGER | PK | No | SERIAL | |
| pago_externo_id | INTEGER | - | Sí | - | |
| metodo_pago | VARCHAR(100) | - | Sí | - | |
| procesador | VARCHAR(100) | - | Sí | - | |
| tipo_pago | VARCHAR(50) | - | Sí | - | |

---

### 📊 dim_periodo_contable
**Registros:** 84

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| periodo_id | INTEGER | PK | No | SERIAL | |
| anio | INTEGER | - | No | - | |
| mes | INTEGER | - | No | - | |
| trimestre | INTEGER | - | No | - | |
| nombre_periodo | VARCHAR(50) | - | Sí | - | |
| fecha_inicio | DATE | - | Sí | - | |
| fecha_fin | DATE | - | Sí | - | |
| cerrado | BOOLEAN | - | Sí | false | |

---

### 📊 dim_producto
**Registros:** 64

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| producto_id | INTEGER | PK | No | SERIAL | |
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
| created_at | TIMESTAMP | - | Sí | NOW() | |

---

### 📊 dim_promocion
**Registros:** 2

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| promocion_id | INTEGER | PK | No | SERIAL | |
| promocion_externo_id | INTEGER | - | Sí | - | |
| codigo | VARCHAR(50) | - | Sí | - | |
| nombre | VARCHAR(255) | - | Sí | - | |
| descripcion | TEXT | - | Sí | - | |
| tipo_descuento | VARCHAR(50) | - | Sí | - | |
| valor_descuento | NUMERIC(10,2) | - | Sí | - | |
| fecha_inicio | DATE | - | Sí | - | |
| fecha_fin | DATE | - | Sí | - | |

---

### 📊 dim_proveedor
**Registros:** 8

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| proveedor_id | INTEGER | PK | No | SERIAL | |
| codigo | VARCHAR(50) | - | Sí | - | |
| nombre | VARCHAR(255) | - | Sí | - | |
| contacto | VARCHAR(255) | - | Sí | - | |
| email | VARCHAR(255) | - | Sí | - | |
| telefono | VARCHAR(50) | - | Sí | - | |
| direccion | VARCHAR(255) | - | Sí | - | |
| ciudad | VARCHAR(100) | - | Sí | - | |
| pais | VARCHAR(100) | - | Sí | - | |
| activo | BOOLEAN | - | Sí | true | |

---

### 📊 dim_sitio_web
**Registros:** 5

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| sitio_id | INTEGER | PK | No | SERIAL | |
| sitio_externo_id | INTEGER | - | Sí | - | |
| codigo | VARCHAR(50) | - | Sí | - | |
| nombre | VARCHAR(255) | - | Sí | - | |
| url | VARCHAR(500) | - | Sí | - | |
| pais | VARCHAR(100) | - | Sí | - | |
| idioma | VARCHAR(10) | - | Sí | - | |
| moneda_default | VARCHAR(3) | - | Sí | - | |
| activo | BOOLEAN | - | Sí | true | |

---

### 📊 dim_tipo_movimiento
**Registros:** 9

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| tipo_movimiento_id | INTEGER | PK | No | SERIAL | |
| codigo | VARCHAR(50) | - | Sí | - | |
| nombre | VARCHAR(100) | - | Sí | - | |
| descripcion | TEXT | - | Sí | - | |
| tipo | VARCHAR(50) | - | Sí | - | |
| afecta_stock | VARCHAR(20) | - | Sí | - | |
| activo | BOOLEAN | - | Sí | true | |

---

### 📊 dim_tipo_transaccion
**Registros:** 9

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| tipo_transaccion_id | INTEGER | PK | No | SERIAL | |
| codigo | VARCHAR(50) | - | Sí | - | |
| nombre | VARCHAR(100) | - | Sí | - | |
| descripcion | TEXT | - | Sí | - | |
| categoria | VARCHAR(50) | - | Sí | - | |
| afecta_flujo | VARCHAR(20) | - | Sí | - | |
| activo | BOOLEAN | - | Sí | true | |

---

### 📊 dim_usuario
**Registros:** 54

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| usuario_id | INTEGER | PK | No | SERIAL | |
| usuario_externo_id | INTEGER | - | Sí | - | |
| username | VARCHAR(255) | - | Sí | - | |
| email | VARCHAR(255) | - | Sí | - | |
| nombre_completo | VARCHAR(255) | - | Sí | - | |
| activo | BOOLEAN | - | Sí | true | |
| created_at | TIMESTAMP | - | Sí | NOW() | |
| updated_at | TIMESTAMP | - | Sí | NOW() | |

---

### 📊 fact_balance
**Registros:** 210

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| balance_id | INTEGER | PK | No | SERIAL | |
| periodo_id | INTEGER | FK | Sí | - | |
| cuenta_id | INTEGER | FK | Sí | - | |
| saldo_inicial | NUMERIC(15,2) | - | Sí | - | |
| debitos | NUMERIC(15,2) | - | Sí | - | |
| creditos | NUMERIC(15,2) | - | Sí | - | |
| saldo_final | NUMERIC(15,2) | - | Sí | - | |
| created_at | TIMESTAMP | - | Sí | NOW() | |

**Foreign Keys:**
- `periodo_id` → `dim_periodo_contable(periodo_id)`
- `cuenta_id` → `dim_cuenta_contable(cuenta_id)`

---

### 📊 fact_estado_resultados
**Registros:** 70

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| resultado_id | INTEGER | PK | No | SERIAL | |
| periodo_id | INTEGER | FK | Sí | - | |
| cuenta_id | INTEGER | FK | Sí | - | |
| centro_costo_id | INTEGER | FK | Sí | - | |
| ingresos | NUMERIC(15,2) | - | Sí | - | |
| costos | NUMERIC(15,2) | - | Sí | - | |
| gastos | NUMERIC(15,2) | - | Sí | - | |
| utilidad_bruta | NUMERIC(15,2) | - | Sí | - | |
| utilidad_neta | NUMERIC(15,2) | - | Sí | - | |
| created_at | TIMESTAMP | - | Sí | NOW() | |

**Foreign Keys:**
- `periodo_id` → `dim_periodo_contable(periodo_id)`
- `cuenta_id` → `dim_cuenta_contable(cuenta_id)`
- `centro_costo_id` → `dim_centro_costo(centro_costo_id)`

---

### 📊 fact_inventario
**Registros:** 408,397

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| movimiento_id | INTEGER | PK | No | SERIAL | |
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
| created_at | TIMESTAMP | - | Sí | NOW() | |

**Foreign Keys:**
- `fecha_id` → `dim_fecha(fecha_id)`
- `producto_id` → `dim_producto(producto_id)`
- `almacen_id` → `dim_almacen(almacen_id)`
- `tipo_movimiento_id` → `dim_tipo_movimiento(tipo_movimiento_id)`
- `proveedor_id` → `dim_proveedor(proveedor_id)`
- `usuario_id` → `dim_usuario(usuario_id)`

---

### 📊 fact_transacciones
**Registros:** 577,640

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| transaccion_id | INTEGER | PK | No | SERIAL | |
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
| created_at | TIMESTAMP | - | Sí | NOW() | |
| periodo_id | INTEGER | FK | Sí | - | |

**Foreign Keys:**
- `fecha_id` → `dim_fecha(fecha_id)`
- `cuenta_id` → `dim_cuenta_contable(cuenta_id)`
- `centro_costo_id` → `dim_centro_costo(centro_costo_id)`
- `tipo_transaccion_id` → `dim_tipo_transaccion(tipo_transaccion_id)`
- `usuario_id` → `dim_usuario(usuario_id)`
- `periodo_id` → `dim_periodo_contable(periodo_id)`

---

### 📊 fact_ventas
**Registros:** 115,528

| Campo | Tipo | Clave | Nullable | Default | Descripción |
|-------|------|-------|----------|---------|-------------|
| venta_id | INTEGER | PK | No | SERIAL | |
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
| created_at | TIMESTAMP | - | Sí | NOW() | |

**Foreign Keys:**
- `fecha_id` → `dim_fecha(fecha_id)`
- `cliente_id` → `dim_cliente(cliente_id)`
- `producto_id` → `dim_producto(producto_id)`
- `orden_id` → `dim_orden(orden_id)`
- `usuario_id` → `dim_usuario(usuario_id)`
- `almacen_id` → `dim_almacen(almacen_id)`

---
