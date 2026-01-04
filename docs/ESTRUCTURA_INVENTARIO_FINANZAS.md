# Estructura de Dimensiones y Facts - Inventario y Finanzas
================================================================

**Proyecto:** Sistema Analítico PuntaFina - Venta de Calzado  
**Fecha:** 16 de Diciembre de 2025  
**Módulos:** Inventario, Finanzas, Costos  

---

## 📦 MÓDULO DE INVENTARIO

### Dimensiones Compartidas

Este módulo utiliza tres **dimensiones conformadas** (compartidas) del módulo de Ventas:

1. **🔗 dim_producto** - Catálogo de productos de calzado
   - Ya existe en el módulo de Ventas
   - Permite vincular movimientos de inventario con ventas
   - Facilita cálculo de costo de ventas y márgenes

2. **🔗 dim_usuario** - Usuarios del sistema
   - Compartida entre Ventas, Inventario y Finanzas
   - Permite rastrear quién registró cada movimiento

3. **🔗 dim_fecha** - Calendario completo
   - Compartida entre todos los módulos
   - Permite análisis temporal integrado

### Dimensiones Propias

### **dim_proveedor**
**Descripción:** Catálogo de proveedores de calzado  
**Grano:** Un registro por proveedor único  

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `id_proveedor` | TEXT PK | Código único del proveedor | PROV001 |
| `nombre_proveedor` | TEXT | Nombre comercial | Calzado Premium SA |
| `razon_social` | TEXT | Razón social completa | Calzado Premium Sociedad Anónima |
| `nit` | TEXT | NIT del proveedor | 0614-123456-001-2 |
| `pais_origen` | TEXT | País de origen | El Salvador |
| `ciudad` | TEXT | Ciudad | San Salvador |
| `direccion` | TEXT | Dirección completa | Col. Escalón, Calle Principal #123 |
| `telefono` | TEXT | Teléfono contacto | +503 2222-3333 |
| `email` | TEXT | Correo electrónico | ventas@calzadopremium.com |
| `contacto_principal` | TEXT | Nombre del contacto | Juan Pérez |
| `dias_credito` | INTEGER | Días de crédito otorgados | 30 |
| `tipo_proveedor` | TEXT | Tipo (nacional/internacional) | nacional |
| `categoria_productos` | TEXT | Categoría de productos | calzado_formal, calzado_deportivo |
| `activo` | BOOLEAN | Proveedor activo | TRUE |
| `fecha_registro` | DATE | Fecha de registro | 2023-01-15 |

---

### **dim_almacen**
**Descripción:** Catálogo de almacenes y tiendas  
**Grano:** Un registro por ubicación física  

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `id_almacen` | TEXT PK | Código único del almacén | ALM_CENTRAL |
| `nombre_almacen` | TEXT | Nombre del almacén | Almacén Central |
| `tipo_almacen` | TEXT | Tipo (bodega/tienda) | bodega |
| `ciudad` | TEXT | Ciudad | San Salvador |
| `departamento` | TEXT | Departamento | San Salvador |
| `direccion` | TEXT | Dirección completa | Zona Industrial, Lote 45 |
| `capacidad_m3` | NUMERIC(10,2) | Capacidad en m³ | 500.00 |
| `encargado` | TEXT | Nombre del encargado | María González |
| `telefono` | TEXT | Teléfono | +503 2111-2222 |
| `activo` | BOOLEAN | Almacén activo | TRUE |
| `fecha_apertura` | DATE | Fecha de apertura | 2023-01-10 |

---

### **dim_movimiento_tipo**
**Descripción:** Catálogo de tipos de movimiento de inventario  
**Grano:** Un registro por tipo de movimiento  

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `id_tipo_movimiento` | TEXT PK | Código único del tipo | MOV_ENTRADA |
| `nombre_tipo` | TEXT | Nombre del tipo | Entrada por Compra |
| `categoria` | TEXT | Categoría (entrada/salida/ajuste) | entrada |
| `afecta_stock` | TEXT | Cómo afecta (suma/resta/ajuste) | suma |
| `descripcion` | TEXT | Descripción detallada | Entrada de mercadería por compra a proveedor |

**Tipos predefinidos:**
- MOV_ENTRADA: Entrada por Compra
- MOV_SALIDA_VENTA: Salida por Venta
- MOV_DEVOLUCION_CLIENTE: Devolución de Cliente (entrada)
- MOV_DEVOLUCION_PROVEEDOR: Devolución a Proveedor (salida)
- MOV_AJUSTE_POSITIVO: Ajuste Positivo (inventario físico mayor)
- MOV_AJUSTE_NEGATIVO: Ajuste Negativo (inventario físico menor)
- MOV_TRASLADO_ENTRADA: Traslado entre Almacenes (entrada)
- MOV_TRASLADO_SALIDA: Traslado entre Almacenes (salida)
- MOV_MERMA: Merma o Pérdida

---

### **fact_inventario**
**Descripción:** Movimientos de inventario  
**Grano:** Línea de movimiento (máximo detalle)  

| Campo | Tipo | Descripción | FK hacia |
|-------|------|-------------|----------|
| `id_movimiento` | SERIAL PK | Clave primaria autoincremental | - |
| `id_producto` | TEXT | ID del producto | 🔗 dim_producto (compartida con Ventas) |
| `id_almacen` | TEXT | ID del almacén | dim_almacen |
| `id_proveedor` | TEXT | ID del proveedor (si aplica) | dim_proveedor |
| `id_tipo_movimiento` | TEXT | Tipo de movimiento | dim_movimiento_tipo |
| `id_fecha` | BIGINT | Fecha del movimiento (YYYYMMDD) | 🔗 dim_fecha (compartida con todos) |
| `id_usuario` | TEXT | Usuario que registró | 🔗 dim_usuario (compartida con todos) |
| `numero_documento` | TEXT | Número de documento de respaldo | - |
| `cantidad` | NUMERIC(10,2) | Cantidad movida | - |
| `costo_unitario` | NUMERIC(10,2) | Costo unitario del producto | - |
| `costo_total` | NUMERIC(15,2) | Costo total del movimiento | - |
| `stock_anterior` | NUMERIC(10,2) | Stock antes del movimiento | - |
| `stock_resultante` | NUMERIC(10,2) | Stock después del movimiento | - |
| `motivo` | TEXT | Motivo del movimiento | - |
| `observaciones` | TEXT | Observaciones adicionales | - |

**Métricas derivadas:**
- Costo promedio ponderado por producto
- Stock mínimo vs stock actual
- Rotación de inventario
- Días de inventario

---

## 💰 MÓDULO DE FINANZAS

### **dim_cuenta_contable**
**Descripción:** Plan de cuentas contable  
**Grano:** Una cuenta contable  

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `id_cuenta` | TEXT PK | Código de la cuenta | 1101 |
| `nombre_cuenta` | TEXT | Nombre de la cuenta | Caja |
| `tipo_cuenta` | TEXT | Tipo (activo/pasivo/patrimonio/ingreso/gasto) | activo |
| `clasificacion` | TEXT | Clasificación (corriente/no corriente) | corriente |
| `cuenta_padre` | TEXT | Cuenta padre (para jerarquía) | 1100 |
| `nivel` | INTEGER | Nivel en la jerarquía | 2 |
| `naturaleza` | TEXT | Naturaleza (deudora/acreedora) | deudora |
| `acepta_movimientos` | BOOLEAN | Acepta movimientos directos | TRUE |
| `estado_financiero` | TEXT | Estado (balance/resultados/flujo) | balance |
| `descripcion` | TEXT | Descripción de la cuenta | Efectivo en caja general |
| `activa` | BOOLEAN | Cuenta activa | TRUE |

**Plan de cuentas sugerido (simplificado):**
```
1000 - ACTIVO
  1100 - Activo Corriente
    1101 - Caja
    1102 - Bancos
    1103 - Cuentas por Cobrar Clientes
    1104 - Inventario de Mercadería
  1200 - Activo No Corriente
    1201 - Mobiliario y Equipo
    1202 - Equipo de Cómputo
    1203 - Edificios
    1204 - Depreciación Acumulada (-)

2000 - PASIVO
  2100 - Pasivo Corriente
    2101 - Cuentas por Pagar Proveedores
    2102 - IVA por Pagar
    2103 - Retenciones por Pagar
  2200 - Pasivo No Corriente
    2201 - Préstamos Bancarios Largo Plazo

3000 - PATRIMONIO
  3101 - Capital Social
  3102 - Utilidades Retenidas
  3103 - Utilidad del Ejercicio

4000 - INGRESOS
  4101 - Ventas
  4102 - Devoluciones sobre Ventas (-)
  4103 - Descuentos sobre Ventas (-)

5000 - COSTO DE VENTAS
  5101 - Costo de Mercadería Vendida

6000 - GASTOS OPERATIVOS
  6100 - Gastos de Venta
    6101 - Sueldos Personal de Ventas
    6102 - Comisiones
    6103 - Publicidad
    6104 - Alquiler de Locales
  6200 - Gastos de Administración
    6201 - Sueldos Personal Administrativo
    6202 - Servicios Públicos
    6203 - Papelería y Útiles
    6204 - Depreciación

7000 - GASTOS FINANCIEROS
  7101 - Intereses Bancarios
  7102 - Comisiones Bancarias
```

---

### **dim_centro_costo**
**Descripción:** Centros de costo para distribución de gastos  
**Grano:** Un centro de costo  

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `id_centro_costo` | TEXT PK | Código del centro de costo | CC_VENTAS |
| `nombre_centro` | TEXT | Nombre del centro | Ventas y Comercialización |
| `tipo_centro` | TEXT | Tipo (operativo/administrativo/ventas) | ventas |
| `responsable` | TEXT | Responsable del centro | Carlos Martínez |
| `activo` | BOOLEAN | Centro activo | TRUE |

**Centros de costo sugeridos:**
- CC_TIENDA_01: Tienda Centro Comercial Metrocentro
- CC_TIENDA_02: Tienda Centro Comercial Multiplaza
- CC_TIENDA_03: Tienda Zona Rosa
- CC_TIENDA_04: Tienda Santa Tecla
- CC_TIENDA_05: Tienda Santa Ana
- CC_ECOMMERCE: Tienda en Línea
- CC_ALMACEN: Almacén Central
- CC_ADMIN: Administración General
- CC_MARKETING: Marketing y Publicidad

---

### **dim_tipo_transaccion**
**Descripción:** Tipos de transacciones contables  
**Grano:** Un tipo de transacción  

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `id_tipo_transaccion` | TEXT PK | Código del tipo | TRX_VENTA |
| `nombre_tipo` | TEXT | Nombre del tipo | Registro de Venta |
| `categoria` | TEXT | Categoría (ingreso/gasto/ajuste) | ingreso |
| `descripcion` | TEXT | Descripción | Registro contable de venta realizada |

**Tipos predefinidos:**
- TRX_VENTA: Registro de Venta
- TRX_COSTO_VENTA: Registro de Costo de Venta
- TRX_COMPRA: Registro de Compra
- TRX_PAGO_PROVEEDOR: Pago a Proveedor
- TRX_COBRO_CLIENTE: Cobro a Cliente
- TRX_GASTO: Registro de Gasto
- TRX_PAGO_PLANILLA: Pago de Planilla
- TRX_DEPRECIACION: Depreciación
- TRX_AJUSTE: Ajuste Contable

---

### **fact_transacciones_contables**
**Descripción:** Asientos contables (partidas dobles)  
**Grano:** Línea de asiento contable  

| Campo | Tipo | Descripción | FK hacia |
|-------|------|-------------|----------|
| `id_asiento` | SERIAL PK | Clave primaria autoincremental | - |
| `numero_asiento` | TEXT | Número de asiento contable | AST-2025-00001 |
| `id_fecha` | BIGINT | Fecha del asiento (YYYYMMDD) | dim_fecha |
| `id_cuenta` | TEXT | Cuenta contable afectada | dim_cuenta_contable |
| `id_centro_costo` | TEXT | Centro de costo (si aplica) | dim_centro_costo |
| `id_tipo_transaccion` | TEXT | Tipo de transacción | dim_tipo_transaccion |
| `id_usuario` | TEXT | Usuario que registró | dim_usuario |
| `tipo_movimiento` | TEXT | Tipo (debe/haber) | debe |
| `monto` | NUMERIC(15,2) | Monto del movimiento | - |
| `documento_referencia` | TEXT | Documento de referencia | FACT-001234 |
| `descripcion` | TEXT | Descripción del asiento | Registro de venta del día |
| `id_venta` | TEXT | Referencia a venta (si aplica) | fact_ventas.id_venta |
| `id_movimiento_inventario` | TEXT | Referencia a movimiento (si aplica) | fact_inventario.id_movimiento |
| `observaciones` | TEXT | Observaciones adicionales | - |

**Restricción:** 
- Por cada `numero_asiento` la suma de debe debe ser igual a la suma de haber

---

### **fact_estado_resultados**
**Descripción:** Estado de Resultados agregado mensual  
**Grano:** Mes + Cuenta + Centro de Costo  

| Campo | Tipo | Descripción | FK hacia |
|-------|------|-------------|----------|
| `id_resultado` | SERIAL PK | Clave primaria | - |
| `año` | INTEGER | Año fiscal | - |
| `mes` | INTEGER | Mes fiscal | - |
| `id_cuenta` | TEXT | Cuenta contable | dim_cuenta_contable |
| `id_centro_costo` | TEXT | Centro de costo | dim_centro_costo |
| `monto_debe` | NUMERIC(15,2) | Total debe del mes | - |
| `monto_haber` | NUMERIC(15,2) | Total haber del mes | - |
| `saldo_neto` | NUMERIC(15,2) | Saldo neto (debe - haber) | - |

**Métricas derivadas:**
- Ventas Netas = Ventas - Devoluciones - Descuentos
- Utilidad Bruta = Ventas Netas - Costo de Ventas
- Margen Bruto % = (Utilidad Bruta / Ventas Netas) * 100
- Utilidad Operativa = Utilidad Bruta - Gastos Operativos
- Utilidad Neta = Utilidad Operativa - Gastos Financieros
- Margen Neto % = (Utilidad Neta / Ventas Netas) * 100

---

### **fact_balance_general**
**Descripción:** Balance General a una fecha  
**Grano:** Fecha + Cuenta  

| Campo | Tipo | Descripción | FK hacia |
|-------|------|-------------|----------|
| `id_balance` | SERIAL PK | Clave primaria | - |
| `id_fecha` | BIGINT | Fecha de corte (YYYYMMDD) | dim_fecha |
| `id_cuenta` | TEXT | Cuenta contable | dim_cuenta_contable |
| `saldo` | NUMERIC(15,2) | Saldo a la fecha | - |
| `tipo_saldo` | TEXT | Tipo (deudor/acreedor) | - |

**Métricas derivadas:**
- Total Activos = Suma de cuentas tipo activo
- Total Pasivos = Suma de cuentas tipo pasivo
- Total Patrimonio = Suma de cuentas tipo patrimonio
- Validación: Activos = Pasivos + Patrimonio

---

## 📊 KPIs y Métricas Clave

### KPIs de Inventario
1. **Costo Promedio de Inventario Mensual**
   - Fórmula: (Inventario Inicial + Inventario Final) / 2
   - Cálculo desde fact_inventario agregado mensualmente

2. **Rotación de Inventario**
   - Fórmula: Costo de Ventas / Costo Promedio Inventario
   - Fuentes: fact_ventas + fact_inventario

3. **Días de Inventario**
   - Fórmula: 365 / Rotación de Inventario
   - Indica cuántos días dura el inventario

4. **Stock Mínimo vs Stock Actual**
   - Alertas de reorden por producto

### KPIs Financieros
1. **Cumplimiento de Meta de Venta Mensual**
   - Fórmula: (Ventas Reales / Meta de Ventas) * mediante **dimensiones conformadas** y referencias cruzadas:

**Dimensiones Conformadas (Compartidas):**
- 🔗 **dim_producto** - Usada en `fact_ventas` y `fact_inventario`
  - Permite vincular ventas con movimientos de inventario
  - Facilita cálculo de costo de ventas
  - Análisis de margen por producto

- 🔗 **dim_usuario** - Usada en todos los módulos
  - Rastreo de responsables por transacción
  - Análisis de productividad por usuario

- 🔗 **dim_fecha** - Usada en todos los módulos
  - Análisis temporal consistente
  - Comparaciones período a período

**Relaciones Directas:**
- `fact_ventas.id_producto` ↔ `fact_inventario.id_producto` → Análisis de costo de ventas
- `fact_ventas.costo_unitario` ← calculado destas) * 100
   - Fuentes: fact_ventas + fact_inventario (costo)

3. **Margen Neto**
   - Fórmula: (Utilidad Neta / Ventas) * 100
   - Fuente: fact_estado_resultados

4. **Razón Corriente**
   - Fórmula: Activo Corriente / Pasivo Corriente
   - Fuente: fact_balance_general

---

## 🔄 Integración con Módulo de Ventas Existente

Las nuevas tablas se integran con las existentes:

**Relaciones:**
- `fact_ventas.id_producto` → vincula con `fact_inventario.id_producto`
- `fact_ventas.costo_unitario` → se obtiene de `fact_inventario.costo_unitario`
- `fact_transacciones_contables.id_venta` → referencia a `fact_ventas.id_venta`
- `fact_transacciones_contables.id_movimiento_inventario` → referencia a `fact_inventario.id_movimiento`

**Flujo de Datos:**
1. Venta se registra en `fact_ventas`
2. Se genera movimiento de salida en `fact_inventario`
3. Se registran asientos contables en `fact_transacciones_contables`:
   - Debe: Cuentas por Cobrar / Caja
   - Haber: Ventas
   - Debe: Costo de Ventas
   - Haber: Inventario

---

## 📁 Archivos CSV de Entrada

Ver archivos template en:
- `/data/inputs/inventario/`
- `/data/inputs/finanzas/`

Cada CSV debe seguir el formato exacto documentado en el siguiente apartado.
