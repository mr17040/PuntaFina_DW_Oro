# 📖 Guía Rápida - Módulos de Inventario y Finanzas

## 🎯 ¿Qué se agregó al ETL?

### ✨ Nuevas Dimensiones (6 propias + 3 compartidas)

**Dimensiones Propias:**
1. **dim_proveedor** - Catálogo de proveedores de calzado
2. **dim_almacen** - Almacenes y tiendas
3. **dim_movimiento_tipo** - Tipos de movimiento de inventario
4. **dim_cuenta_contable** - Plan de cuentas contable
5. **dim_centro_costo** - Centros de costo
6. **dim_tipo_transaccion** - Tipos de transacción contable

**Dimensiones Compartidas con Ventas (Dimensiones Conformadas):**
- 🔗 **dim_producto** - Catálogo de productos (usada en Ventas e Inventario)
- 🔗 **dim_usuario** - Usuarios del sistema (usada en Ventas, Inventario y Finanzas)
- 🔗 **dim_fecha** - Calendario (usada en todos los módulos)

### ✨ Nuevas Tablas de Hechos (4)
1. **fact_inventario** - Movimientos de inventario
2. **fact_transacciones_contables** - Asientos contables
3. **fact_estado_resultados** - Estado de resultados agregado mensual
4. **fact_balance_general** - Balance general a fecha

---

## 📁 Estructura de Carpetas CSV

```
data/inputs/
├── inventario/
│   ├── proveedores.csv            ← Completar con sus proveedores
│   ├── almacenes.csv              ← Completar con sus ubicaciones
│   ├── tipos_movimiento.csv       ← NO MODIFICAR (predefinido)
│   └── movimientos_inventario.csv ← Completar con movimientos
│
└── finanzas/
    ├── cuentas_contables.csv      ← Completar con plan de cuentas
    ├── centros_costo.csv          ← Completar con centros de costo
    ├── tipos_transaccion.csv      ← NO MODIFICAR (predefinido)
    └── transacciones_contables.csv ← Completar con asientos
```

---

## 🚀 Cómo Usar

### Paso 1: Completar los CSV

#### Inventario
1. **proveedores.csv** - Liste todos sus proveedores
   ```csv
   id_proveedor,nombre_proveedor,razon_social,nit,...
   PROV001,Calzado Premium SA,Calzado Premium SA de CV,0614-123456-001-2,...
   ```

2. **almacenes.csv** - Liste todos sus almacenes y tiendas
   ```csv
   id_almacen,nombre_almacen,tipo_almacen,ciudad,...
   ALM_CENTRAL,Almacén Central,bodega,San Salvador,...
   TIENDA_01,Tienda Metrocentro,tienda,San Salvador,...
   ```

3. **movimientos_inventario.csv** - Registre todos los movimientos
   ```csv
   id_producto,id_almacen,id_proveedor,id_tipo_movimiento,fecha_movimiento,...
   1,ALM_CENTRAL,PROV001,MOV_ENTRADA,2024-01-15,...
   ```

#### Finanzas
1. **cuentas_contables.csv** - Defina su plan de cuentas
   ```csv
   id_cuenta,nombre_cuenta,tipo_cuenta,nivel,naturaleza,...
   1101,Caja,activo,3,deudora,...
   4101,Ventas,ingreso,2,acreedora,...
   ```

2. **centros_costo.csv** - Defina sus centros de costo
   ```csv
   id_centro_costo,nombre_centro,tipo_centro,responsable,...
   CC_TIENDA_01,Tienda Metrocentro,ventas,Pedro Hernández,...
   ```

3. **transacciones_contables.csv** - Registre asientos contables
   ```csv
   numero_asiento,fecha_asiento,id_cuenta,tipo_movimiento,monto,...
   AST-2024-00001,2024-01-20,1102,debe,225.00,...
   AST-2024-00001,2024-01-20,4101,haber,225.00,...
   ```

### Paso 2: Ejecutar el ETL

```bash
cd scripts
python orquestador_maestro.py
```

Esto ejecutará:
1. ✅ Dimensiones de Ventas
2. ✅ Fact de Ventas
3. ✨ **Dimensiones y Facts de Inventario y Finanzas** (NUEVO)
4. ✅ Creación de todas las tablas en PostgreSQL

### Paso 3: Verificar los Resultados

Los archivos se generarán en:
- `data/outputs/parquet/` - Formato optimizado
- `data/outputs/csv/` - Para revisión

---

## 📊 Consultas de Ejemplo

### Inventario
```sql
-- Stock actual por producto
SELECT 
    p.nombre,
    a.nombre_almacen,
    i.stock_resultante,
    i.costo_unitario,
    i.stock_resultante * i.costo_unitario as valor_inventario
FROM fact_inventario i
JOIN dim_producto p ON i.id_producto = p.id_producto
JOIN dim_almacen a ON i.id_almacen = a.id_almacen
WHERE i.id_fecha = (SELECT MAX(id_fecha) FROM fact_inventario)
ORDER BY p.nombre, a.nombre_almacen;
```

### Finanzas
```sql
-- Estado de Resultados del Mes
SELECT 
    c.nombre_cuenta,
    c.tipo_cuenta,
    SUM(e.saldo_neto) as saldo
FROM fact_estado_resultados e
JOIN dim_cuenta_contable c ON e.id_cuenta = c.id_cuenta
WHERE e.año = 2024 AND e.mes = 12
GROUP BY c.nombre_cuenta, c.tipo_cuenta
ORDER BY c.tipo_cuenta, c.nombre_cuenta;
```

---

## ⚠️ Validaciones Importantes

### Inventario
✅ **Stock Anterior + Movimiento = Stock Resultante**
✅ **Costo Total = Cantidad × Costo Unitario**
✅ **IDs de productos y almacenes deben existir**

### Finanzas
✅ **Por cada asiento: Debe = Haber**
✅ **Cuentas de activo tienen naturaleza deudora**
✅ **Cuentas de pasivo/patrimonio tienen naturaleza acreedora**

---

## 📖 Documentación Completa

Para más detalles, consulte:
1. [ESTRUCTURA_INVENTARIO_FINANZAS.md](docs/ESTRUCTURA_INVENTARIO_FINANZAS.md) - Estructura detallada
2. [GUIA_USO_INVENTARIO_FINANZAS.md](docs/GUIA_USO_INVENTARIO_FINANZAS.md) - Guía de uso completa
3. [RESUMEN_MODELO_COMPLETO.md](docs/RESUMEN_MODELO_COMPLETO.md) - Modelo dimensional completo

---

## 🎯 KPIs Disponibles

### Inventario
- ✅ Costo promedio de inventario mensual
- ✅ Rotación de inventario
- ✅ Días de inventario
- ✅ Stock mínimo vs stock actual

### Finanzas
- ✅ Ventas Netas
- ✅ Utilidad Bruta
- ✅ Margen Bruto %
- ✅ Utilidad Neta
- ✅ Margen Neto %
- ✅ Razón Corriente

---

## 🆘 Solución de Problemas

### Error: "Archivo no encontrado"
→ Verifique que los archivos CSV estén en `data/inputs/inventario/` y `data/inputs/finanzas/`

### Error: "Debe ≠ Haber en asiento"
→ Revise su archivo `transacciones_contables.csv`, la suma de debe debe ser igual a la suma de haber para cada `numero_asiento`

### Error: "ID no existe en dimensión"
→ Asegúrese de que los IDs referenciados (productos, almacenes, cuentas, etc.) existan en las dimensiones correspondientes

---

## 📞 Próximos Pasos

1. ✅ Complete los archivos CSV con sus datos reales
2. ✅ Ejecute el ETL con `python orquestador_maestro.py`
3. ✅ Valide los datos con las consultas SQL de ejemplo
4. ✅ Conecte Power BI para crear dashboards
5. ✅ Comience a tomar decisiones basadas en datos!

---

**Fecha de actualización:** 16 de Diciembre de 2025  
**Versión:** 2.0 - Incluye Inventario y Finanzas
