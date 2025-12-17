# Guía de Uso - Módulos de Inventario y Finanzas

## 📦 Módulo de Inventario

### Archivos CSV de Entrada

#### 1. `proveedores.csv`
Registre todos los proveedores de calzado.

**Campos:**
- `id_proveedor`: Código único (ej: PROV001, PROV002)
- `nombre_proveedor`: Nombre comercial
- `razon_social`: Razón social completa
- `nit`: NIT del proveedor
- `pais_origen`: País de origen
- `ciudad`: Ciudad
- `direccion`: Dirección completa
- `telefono`: Teléfono con código de país
- `email`: Correo electrónico
- `contacto_principal`: Nombre del contacto
- `dias_credito`: Días de crédito (número entero)
- `tipo_proveedor`: nacional o internacional
- `categoria_productos`: Categorías separadas por comas
- `activo`: TRUE o FALSE
- `fecha_registro`: Formato YYYY-MM-DD

**Ejemplo:**
```csv
id_proveedor,nombre_proveedor,razon_social,nit,pais_origen,ciudad,direccion,telefono,email,contacto_principal,dias_credito,tipo_proveedor,categoria_productos,activo,fecha_registro
PROV001,Calzado Premium SA,Calzado Premium Sociedad Anónima,0614-123456-001-2,El Salvador,San Salvador,Col. Escalón Calle Principal #123,+503 2222-3333,ventas@calzadopremium.com,Juan Pérez,30,nacional,"calzado_formal,calzado_deportivo",TRUE,2023-01-15
```

---

#### 2. `almacenes.csv`
Registre todas las ubicaciones (bodegas y tiendas).

**Campos:**
- `id_almacen`: Código único (ej: ALM_CENTRAL, TIENDA_01)
- `nombre_almacen`: Nombre del almacén o tienda
- `tipo_almacen`: bodega o tienda
- `ciudad`: Ciudad
- `departamento`: Departamento
- `direccion`: Dirección completa
- `capacidad_m3`: Capacidad en metros cúbicos (número decimal)
- `encargado`: Nombre del encargado
- `telefono`: Teléfono con código de país
- `activo`: TRUE o FALSE
- `fecha_apertura`: Formato YYYY-MM-DD

**Ejemplo:**
```csv
id_almacen,nombre_almacen,tipo_almacen,ciudad,departamento,direccion,capacidad_m3,encargado,telefono,activo,fecha_apertura
ALM_CENTRAL,Almacén Central,bodega,San Salvador,San Salvador,Zona Industrial Lote 45,500.00,María González,+503 2111-2222,TRUE,2023-01-10
TIENDA_01,Tienda Metrocentro,tienda,San Salvador,San Salvador,Centro Comercial Metrocentro Local 234,80.00,Pedro Hernández,+503 2333-4444,TRUE,2023-01-15
```

---

#### 3. `tipos_movimiento.csv`
**NO MODIFICAR** - Este archivo contiene los tipos de movimiento predefinidos.

Tipos disponibles:
- `MOV_ENTRADA`: Entrada por Compra
- `MOV_SALIDA_VENTA`: Salida por Venta
- `MOV_DEVOLUCION_CLIENTE`: Devolución de Cliente
- `MOV_DEVOLUCION_PROVEEDOR`: Devolución a Proveedor
- `MOV_AJUSTE_POSITIVO`: Ajuste Positivo
- `MOV_AJUSTE_NEGATIVO`: Ajuste Negativo
- `MOV_TRASLADO_ENTRADA`: Traslado Entrada
- `MOV_TRASLADO_SALIDA`: Traslado Salida
- `MOV_MERMA`: Merma o Pérdida

---

#### 4. `movimientos_inventario.csv`
Registre todos los movimientos de inventario.

**Campos:**
- `id_producto`: ID del producto (debe existir en dim_producto)
- `id_almacen`: ID del almacén (ej: ALM_CENTRAL, TIENDA_01)
- `id_proveedor`: ID del proveedor (dejar vacío si no aplica)
- `id_tipo_movimiento`: Tipo de movimiento (usar códigos de tipos_movimiento.csv)
- `fecha_movimiento`: Formato YYYY-MM-DD
- `id_usuario`: ID del usuario que registró (debe existir en dim_usuario)
- `numero_documento`: Número de documento de respaldo (ej: COMP-2024-001)
- `cantidad`: Cantidad movida (número decimal)
- `costo_unitario`: Costo por unidad (número decimal)
- `costo_total`: Costo total del movimiento (número decimal)
- `stock_anterior`: Stock antes del movimiento (número decimal)
- `stock_resultante`: Stock después del movimiento (número decimal)
- `motivo`: Motivo del movimiento
- `observaciones`: Observaciones adicionales

**Ejemplo:**
```csv
id_producto,id_almacen,id_proveedor,id_tipo_movimiento,fecha_movimiento,id_usuario,numero_documento,cantidad,costo_unitario,costo_total,stock_anterior,stock_resultante,motivo,observaciones
1,ALM_CENTRAL,PROV001,MOV_ENTRADA,2024-01-15,1,COMP-2024-001,100,35.50,3550.00,0,100,Compra inicial de inventario,Primera compra del año
1,TIENDA_01,,,MOV_TRASLADO_ENTRADA,2024-01-16,1,TRASL-001,30,35.50,1065.00,0,30,Traslado para surtir tienda,Desde almacén central
```

---

## 💰 Módulo de Finanzas

### Archivos CSV de Entrada

#### 1. `cuentas_contables.csv`
Plan de cuentas contable de la empresa.

**Campos:**
- `id_cuenta`: Código de cuenta (ej: 1101, 4101)
- `nombre_cuenta`: Nombre de la cuenta
- `tipo_cuenta`: activo, pasivo, patrimonio, ingreso, costo, gasto, gasto_financiero
- `clasificacion`: corriente, no_corriente (o vacío)
- `cuenta_padre`: Código de cuenta padre (o vacío si es cuenta principal)
- `nivel`: Nivel en la jerarquía (1, 2, 3, etc.)
- `naturaleza`: deudora o acreedora
- `acepta_movimientos`: TRUE o FALSE
- `estado_financiero`: balance, resultados, flujo
- `descripcion`: Descripción de la cuenta
- `activa`: TRUE o FALSE

**Ejemplo:**
```csv
id_cuenta,nombre_cuenta,tipo_cuenta,clasificacion,cuenta_padre,nivel,naturaleza,acepta_movimientos,estado_financiero,descripcion,activa
1000,ACTIVO,activo,,,1,deudora,FALSE,balance,Grupo principal de activos,TRUE
1101,Caja,activo,corriente,1100,3,deudora,TRUE,balance,Efectivo en caja general,TRUE
4101,Ventas,ingreso,,4000,2,acreedora,TRUE,resultados,Ingresos por ventas de calzado,TRUE
```

---

#### 2. `centros_costo.csv`
Centros de costo para distribución de gastos.

**Campos:**
- `id_centro_costo`: Código único (ej: CC_TIENDA_01)
- `nombre_centro`: Nombre del centro de costo
- `tipo_centro`: ventas, operativo, administrativo
- `responsable`: Nombre del responsable
- `activo`: TRUE o FALSE

**Ejemplo:**
```csv
id_centro_costo,nombre_centro,tipo_centro,responsable,activo
CC_TIENDA_01,Tienda Centro Comercial Metrocentro,ventas,Pedro Hernández,TRUE
CC_ADMIN,Administración General,administrativo,Jorge Rivas,TRUE
```

---

#### 3. `tipos_transaccion.csv`
**NO MODIFICAR** - Este archivo contiene los tipos de transacción predefinidos.

Tipos disponibles:
- `TRX_VENTA`: Registro de Venta
- `TRX_COSTO_VENTA`: Registro de Costo de Venta
- `TRX_COMPRA`: Registro de Compra
- `TRX_PAGO_PROVEEDOR`: Pago a Proveedor
- `TRX_COBRO_CLIENTE`: Cobro a Cliente
- `TRX_GASTO`: Registro de Gasto
- `TRX_PAGO_PLANILLA`: Pago de Planilla
- `TRX_DEPRECIACION`: Depreciación
- `TRX_AJUSTE`: Ajuste Contable

---

#### 4. `transacciones_contables.csv`
Registre todos los asientos contables.

**IMPORTANTE:** Por cada `numero_asiento`, la suma de debe debe ser igual a la suma de haber.

**Campos:**
- `numero_asiento`: Número único de asiento (ej: AST-2024-00001)
- `fecha_asiento`: Formato YYYY-MM-DD
- `id_cuenta`: Cuenta contable afectada
- `id_centro_costo`: Centro de costo (o vacío si no aplica)
- `id_tipo_transaccion`: Tipo de transacción
- `id_usuario`: Usuario que registró
- `tipo_movimiento`: debe o haber
- `monto`: Monto del movimiento (número decimal)
- `documento_referencia`: Documento de referencia (ej: FACT-001)
- `descripcion`: Descripción del asiento
- `id_venta`: Referencia a venta (o vacío)
- `id_movimiento_inventario`: Referencia a movimiento de inventario (o vacío)
- `observaciones`: Observaciones adicionales

**Ejemplo:**
```csv
numero_asiento,fecha_asiento,id_cuenta,id_centro_costo,id_tipo_transaccion,id_usuario,tipo_movimiento,monto,documento_referencia,descripcion,id_venta,id_movimiento_inventario,observaciones
AST-2024-00001,2024-01-20,1102,CC_TIENDA_01,TRX_VENTA,2,debe,225.00,FACT-001,Registro de venta - Tienda Metrocentro,,,Venta de contado
AST-2024-00001,2024-01-20,4101,CC_TIENDA_01,TRX_VENTA,2,haber,200.00,FACT-001,Registro de venta - Tienda Metrocentro,,,Subtotal venta
AST-2024-00001,2024-01-20,2102,CC_TIENDA_01,TRX_VENTA,2,haber,25.00,FACT-001,IVA cobrado sobre venta,,,IVA 13%
```

---

## 🚀 Ejecución del ETL

### Opción 1: Ejecutar todo el pipeline
```bash
cd scripts
python orquestador_maestro.py
```

Esto ejecutará en orden:
1. Construcción de dimensiones de Ventas
2. Construcción de fact_ventas
3. **Construcción de dimensiones y hechos de Inventario y Finanzas**
4. Creación de todas las tablas en la base de datos

### Opción 2: Ejecutar solo Inventario y Finanzas
```bash
cd scripts
python build_inventario_finanzas.py
```

Esto construirá:
- **Dimensiones:** dim_proveedor, dim_almacen, dim_movimiento_tipo, dim_cuenta_contable, dim_centro_costo, dim_tipo_transaccion
- **Hechos:** fact_inventario, fact_transacciones_contables, fact_estado_resultados, fact_balance_general

---

## 📁 Ubicación de Archivos

### Archivos de Entrada (CSV)
```
data/inputs/inventario/
├── proveedores.csv
├── almacenes.csv
├── tipos_movimiento.csv
└── movimientos_inventario.csv

data/inputs/finanzas/
├── cuentas_contables.csv
├── centros_costo.csv
├── tipos_transaccion.csv
└── transacciones_contables.csv
```

### Archivos de Salida
```
data/outputs/parquet/
├── dim_proveedor.parquet
├── dim_almacen.parquet
├── dim_movimiento_tipo.parquet
├── dim_cuenta_contable.parquet
├── dim_centro_costo.parquet
├── dim_tipo_transaccion.parquet
├── fact_inventario.parquet
├── fact_transacciones_contables.parquet
├── fact_estado_resultados.parquet
└── fact_balance_general.parquet

data/outputs/csv/
└── (mismos archivos en formato CSV para revisión)
```

---

## ⚠️ Validaciones Importantes

### Inventario
1. **Stock Anterior + Movimiento = Stock Resultante**
   - Para entradas: `stock_resultante = stock_anterior + cantidad`
   - Para salidas: `stock_resultante = stock_anterior - cantidad`

2. **Costo Total = Cantidad × Costo Unitario**

3. **IDs de productos y almacenes deben existir** en las dimensiones correspondientes

### Finanzas
1. **Por cada número de asiento, Debe = Haber**
   - Suma de montos con `tipo_movimiento = 'debe'` debe ser igual a suma de `tipo_movimiento = 'haber'`

2. **Cuentas de Balance:**
   - Activos: naturaleza deudora
   - Pasivos: naturaleza acreedora
   - Patrimonio: naturaleza acreedora

3. **Cuentas de Resultados:**
   - Ingresos: naturaleza acreedora
   - Gastos y Costos: naturaleza deudora

---

## 📊 KPIs Calculados Automáticamente

### Inventario
- Costo promedio de inventario mensual
- Rotación de inventario
- Días de inventario
- Stock mínimo vs stock actual

### Finanzas
- Ventas Netas = Ventas - Devoluciones - Descuentos
- Utilidad Bruta = Ventas Netas - Costo de Ventas
- Margen Bruto % = (Utilidad Bruta / Ventas Netas) × 100
- Utilidad Neta
- Margen Neto %
- Razón Corriente = Activo Corriente / Pasivo Corriente

---

## 🔍 Validación de Datos

Después de ejecutar el ETL, puede validar los datos con estas consultas SQL:

```sql
-- Verificar dimensiones cargadas
SELECT 'dim_proveedor' as tabla, COUNT(*) as registros FROM dim_proveedor
UNION ALL
SELECT 'dim_almacen', COUNT(*) FROM dim_almacen
UNION ALL
SELECT 'dim_cuenta_contable', COUNT(*) FROM dim_cuenta_contable;

-- Verificar movimientos de inventario
SELECT 
    id_tipo_movimiento,
    COUNT(*) as movimientos,
    SUM(costo_total) as costo_total
FROM fact_inventario
GROUP BY id_tipo_movimiento;

-- Verificar balance de asientos contables
SELECT 
    numero_asiento,
    SUM(CASE WHEN tipo_movimiento = 'debe' THEN monto ELSE 0 END) as total_debe,
    SUM(CASE WHEN tipo_movimiento = 'haber' THEN monto ELSE 0 END) as total_haber,
    SUM(CASE WHEN tipo_movimiento = 'debe' THEN monto ELSE -monto END) as diferencia
FROM fact_transacciones_contables
GROUP BY numero_asiento
HAVING ABS(SUM(CASE WHEN tipo_movimiento = 'debe' THEN monto ELSE -monto END)) > 0.01;
```

---

## 📞 Soporte

Para preguntas o problemas, revise:
1. [ESTRUCTURA_INVENTARIO_FINANZAS.md](ESTRUCTURA_INVENTARIO_FINANZAS.md) - Documentación completa
2. Logs en `logs/pipeline_YYYYMMDD_HHMMSS.log`
3. Archivos de ejemplo en `data/inputs/`
