# 🗺️ Diagrama del Modelo Dimensional - Data Warehouse PuntaFina

## Modelo Estrella Completo: 19 Dimensiones + 5 Facts

```
═══════════════════════════════════════════════════════════════════════════════════
                         MÓDULO DE VENTAS (Existente)
═══════════════════════════════════════════════════════════════════════════════════

    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
    │ dim_fecha   │     │ dim_cliente │     │ dim_producto│     │ dim_usuario │
    │             │     │             │     │             │     │             │
    │ PK: id_fecha│     │ PK: id_cli  │     │ PK: id_prod │     │ PK: id_usr  │
    └──────┬──────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
           │                   │                   │                   │
           │                   │                   │                   │
    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
    │dim_sitio_web│     │  dim_canal  │     │ dim_direccion│    │  dim_envio  │
    │             │     │             │     │             │     │             │
    │ PK: id_sitio│     │ PK: id_canal│     │ PK: id_direc│     │ PK: id_envio│
    └──────┬──────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
           │                   │                   │                   │
           │                   │                   │                   │
    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
    │  dim_pago   │     │dim_impuestos│     │dim_promocion│     │  dim_orden  │
    │             │     │             │     │             │     │             │
    │ PK: id_pago │     │ PK: id_impto│     │ PK: id_promo│     │ PK: id_orden│
    └──────┬──────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
           │                   │                   │                   │
           │                   │                   │                   │
    ┌─────────────┐                                                    │
    │dim_line_item│                                                    │
    │             │                                                    │
    │PK: id_line  │                                                    │
    └──────┬──────┘                                                    │
           │                                                           │
           └────────────────────┬──────────────────────────────────────┘
                                │
                   ┌────────────▼────────────┐
                   │    fact_ventas          │
                   │                         │
                   │ PK: id_venta (SERIAL)   │
                   │ FK: id_fecha            │
                   │ FK: id_cliente          │
                   │ FK: id_producto         │◄─────────────┐
                   │ FK: id_usuario          │              │
                   │ FK: id_sitio_web        │              │
                   │ FK: id_canal            │              │
                   │ FK: id_direccion        │              │
                   │ FK: id_envio            │              │
                   │ FK: id_pago             │              │
                   │ FK: id_impuestos        │              │
                   │ FK: id_promocion        │              │
                   │ FK: id_orden            │              │
                   │ FK: id_line_item        │              │
                   │ ------------------------│              │
                   │ cantidad                │              │
                   │ precio_unitario         │              │
                   │ total_linea             │              │
                   │ total_linea_neto        │              │
                   │ descuento_promocion     │              │
                   │ stock_inicial           │              │
                   │ stock_restante          │              │
                   └─────────────────────────┘              │
                                                            │
═══════════════════════════════════════════════════════════════════════════════════
                         MÓDULO DE INVENTARIO (Nuevo)
═══════════════════════════════════════════════════════════════════════════════════

    ┌─────────────────────┐     ┌──────────────────────┐     ┌─────────────────────┐
    │   dim_proveedor     │     │    dim_almacen       │     │ dim_movimiento_tipo │
    │                     │     │                      │     │                     │
    │ PK: id_proveedor    │     │ PK: id_almacen       │     │ PK: id_tipo_mov     │
    │                     │     │                      │     │                     │
    │                     │     │                      │     │                     │
    └──────────┬──────────┘     └──────────┬───────────┘     └──────────┬──────────┘
               │                           │                            │
               │                           │                            │
    ┌──────────────────────────────────────────────────────────────────────────────┐
    │  DIMENSIONES COMPARTIDAS (desde módulo Ventas)                               │
    │  🔗 dim_producto - Catálogo de productos                                     │
    │  🔗 dim_usuario - Usuarios del sistema                                       │
    │  🔗 dim_fecha - Calendario completo                                          │
    └──────────────────────────────────┬───────────────────────────────────────────┘
                                       │
               ┌───────────────────────┴───────────────────────┐
    │                     │     │                      │     │                     │
    │ nombre_proveedor    │     │ nombre_almacen       │     │ nombre_tipo         │
    │ razon_social        │     │ tipo_almacen         │     │ categoria           │
    │ nit                 │     │ ciudad               │     │ afecta_stock        │
    │ pais_origen         │     │ departamento         │     │ descripcion         │
    │ ciudad              │     │ capacidad_m3         │     │                     │
    │ dias_credito        │     │ encargado            │     │ Tipos:              │
    │ tipo_proveedor      │     │                      │     │ - MOV_ENTRADA       │
    │ categoria_productos │     │ Tipos:               │     │ - MOV_SALIDA_VENTA  │
    │ activo              │     │ - bodega             │     │ - MOV_DEVOLUCION    │
    └──────────┬──────────┘     │ - tienda             │     │ - MOV_AJUSTE        │
               │                └──────────┬───────────┘     │ - MOV_TRASLADO      │
               │                           │                 │ - MOV_MERMA         │
               │                           │                 └──────────┬──────────┘
               │                           │                            │
               └───────────────┬───────────┴────────────────────────────┘
                               │
                  ┌────────────▼────────────┐
                  │   fact_inventario       │
                  │                         │
                  │ PK: id_movimiento       │
                  │ FK: id_producto         │───────────────┘
                  │ FK: id_almacen          │
                  │ FK: id_proveedor        │
                  │ FK: id_tipo_movimiento  │
                  │ FK: id_fecha            │
                  │ FK: id_usuario          │
                  │ ------------------------│
                  │ numero_documento        │
                  │ cantidad                │
                  │ costo_unitario          │
                  │ costo_total             │
                  │ stock_anterior          │
                  │ stock_resultante        │
                  │ motivo                  │
                  │ observaciones           │
                  └─────────────────────────┘
                               │
                               │ (Integración)
                               │
═══════════════════════════════════════════════════════════════════════════════════
                         MÓDULO DE FINANZAS (Nuevo)
═══════════════════════════════════════════════════════════════════════════════════

    ┌────────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
    │ dim_cuenta_contable    │    │  dim_centro_costo   │    │ dim_tipo_transaccion│
    │                        │    │                     │    │                     │
    │ PK: id_cuenta          │    │ PK: id_centro_costo │    │ PK: id_tipo_trx     │
    │                        │    │                     │    │                     │
    │ nombre_cuenta          │    │ nombre_centro       │    │ nombre_tipo         │
    │ tipo_cuenta            │    │ tipo_centro         │    │ categoria           │
    │ clasificacion          │    │ responsable         │    │ descripcion         │
    │ cuenta_padre           │    │                     │    │                     │
    │ nivel                  │    │ Tipos:              │    │ Tipos:              │
    │ naturaleza             │    │ - ventas            │    │ - TRX_VENTA         │
    │ acepta_movimientos     │    │ - operativo         │    │ - TRX_COSTO_VENTA   │
    │ estado_financiero      │    │ - administrativo    │    │ - TRX_COMPRA        │
    │                        │    │                     │    │ - TRX_PAGO          │
    │ Tipos:                 │    │ Ejemplos:           │    │ - TRX_GASTO         │
    │ - activo               │    │ - CC_TIENDA_01      │    │ - TRX_DEPRECIACION  │
    │ - pasivo               │    │ - CC_ECOMMERCE      │    │ - TRX_AJUSTE        │
    │ - patrimonio           │    │ - CC_ALMACEN        │    │                     │
    │ - ingreso              │    │ - CC_ADMIN          │    │                     │
    │ - costo                │    │ - CC_MARKETING      │    │                     │
    │ - gasto                │    │                     │    │                     │
    └──────────┬─────────────┘    └──────────┬──────────┘    └──────────┬──────────┘
               │                             │                          │
               └─────────────────┬───────────┴──────────────────────────┘
                                 │
                    ┌────────────▼──────────────┐
                    │ fact_transacciones_       │
                    │      contables            │
                    │                           │
                    │ PK: id_asiento (SERIAL)   │
                    │ FK: id_fecha              │
                    │ FK: id_cuenta             │
                    │ FK: id_centro_costo       │
                    │ FK: id_tipo_transaccion   │
                    │ FK: id_usuario            │
                    │ ---------------------------│
                    │ numero_asiento            │
                    │ tipo_movimiento (debe/    │
                    │                  haber)   │
                    │ monto                     │
                    │ documento_referencia      │
                    │ descripcion               │
                    │ id_venta (opcional)       │
                    │ id_movimiento_inventario  │
                    │         (opcional)        │
                    └─────┬─────────────────────┘
                          │
              ┌───────────┴───────────┐
              │                       │
              ▼                       ▼
    ┌─────────────────────┐    ┌──────────────────────┐
    │ fact_estado_        │    │ fact_balance_        │
    │    resultados       │    │    general           │
    │                     │    │                      │
    │ PK: id_resultado    │    │ PK: id_balance       │
    │ FK: id_cuenta       │    │ FK: id_fecha         │
    │ FK: id_centro_costo │    │ FK: id_cuenta        │
    │                     │    │                      │
    │ año                 │    │ saldo                │
    │ mes                 │    │ tipo_saldo           │
    │ monto_debe          │    │ (deudor/acreedor)    │
    │ monto_haber         │    │                      │
    │ saldo_neto          │    │                      │
    │                     │    │                      │
    │ (Agregado mensual)  │    │ (Saldo acumulado)    │
    └─────────────────────┘    └──────────────────────┘

═══════════════════════════════════════════════════════════════════════════════════
                         INTEGRACIÓN ENTRE MÓDULOS
═══════════════════════════════════════════════════════════════════════════════════

    fact_ventas.id_producto ─────► dim_producto ◄───── fact_inventario.id_producto
          │                                                     │
          │                                                     │
          └──► Costo de Ventas = cantidad × costo_unitario ◄───┘
          
    
    fact_ventas ──────────► fact_transacciones_contables
         │                           │
         │                           │
         └──► id_venta ──────────────┘
          🔗 Compartida (todos los módulos)
  ├─ dim_cliente             (~5,000)             - Clientes únicos
  ├─ dim_producto            (~500)               - Catálogo de calzado 🔗 Compartida (Ventas/Inventario)
  ├─ dim_usuario             (~50)                - Usuarios del sistema 🔗 Compartida (Ventas/Inventario/Finanzas)
         │                           │
         └──► id_movimiento_inv ─────┘


═══════════════════════════════════════════════════════════════════════════════════
                         RESUMEN DE CARDINALIDADES
═══════════════════════════════════════════════════════════════════════════════════

DIMENSIONES:
  ├─ dim_fecha               (~1,100 registros)   - Calendario 2023-2025
  ├─ dim_cliente             (~5,000)             - Clientes únicos
  ├─ dim_producto            (~500)               - Catálogo de calzado
  ├─ dim_usuario             (~50)                - Usuarios del sistema
  ├─ dim_sitio_web           (~7)                 - Tiendas + ecommerce
  ├─ dim_canal               (~10)                - Canales de venta
  ├─ dim_direccion           (~2,000)             - Direcciones de envío
  ├─ dim_envio               (~15)                - Métodos de envío
  ├─ dim_pago                (~5)                 - Métodos de pago
  ├─ dim_impuestos           (~5)                 - Configuración fiscal
  ├─ dim_promocion           (~50)                - Promociones
  ├─ dim_orden               (~10,000)            - Órdenes únicas
  ├─ dim_line_item           (~30,000)            - Líneas de pedido
  ├─ dim_proveedor           (~20)         ✨ NUEVO - Proveedores
  ├─ dim_almacen             (~7)          ✨ NUEVO - Almacenes/tiendas
  ├─ dim_movimiento_tipo     (9)           ✨ NUEVO - Tipos de movimiento
  ├─ dim_cuenta_contable     (~40)         ✨ NUEVO - Plan de cuentas
  ├─ dim_centro_costo        (~9)          ✨ NUEVO - Centros de costo
  └─ dim_tipo_transaccion    (9)           ✨ NUEVO - Tipos de transacción

FACTS:
  ├─ fact_ventas                     (~30,000)    - Transacciones de venta
  ├─ fact_inventario                 (~100,000)   ✨ NUEVO - Movimientos
  ├─ fact_transacciones_contables    (~200,000)   ✨ NUEVO - Asientos
  ├─ fact_estado_resultados          (~1,000)     ✨ NUEVO - Estado mensual
  └─ fact_balance_general            (~2,000)     ✨ NUEVO - Balance a fecha

TOTAL: 19 Dimensiones + 5 Facts = 24 Tablas

═══════════════════════════════════════════════════════════════════════════════════
```

## 🎯 KPIs y Métricas Calculables

### Del Módulo de Ventas
- ✅ Ventas diarias/mensuales/anuales
- ✅ Top productos más vendidos
- ✅ Top clientes más importantes
- ✅ Ventas por canal
- ✅ Ventas por tienda
- ✅ Ticket promedio
- ✅ Cumplimiento de meta de ventas

### Del Módulo de Inventario
- ✅ Stock actual por producto y almacén
- ✅ Costo promedio de inventario mensual
- ✅ Rotación de inventario
- ✅ Días de inventario
- ✅ Movimientos de entrada/salida
- ✅ Valorización de inventario
- ✅ Stock mínimo vs stock actual

### Del Módulo de Finanzas
- ✅ Estado de Resultados mensual
- ✅ Balance General a fecha
- ✅ Margen Bruto %
- ✅ Margen Neto %
- ✅ Utilidad Bruta
- ✅ Utilidad Neta
- ✅ Gastos por centro de costo
- ✅ Razón Corriente
- ✅ ROI por producto

### Métricas Integradas (Cross-Module)
- ✅ Costo de Ventas = Ventas × Costo Unitario Promedio
- ✅ Margen por Producto = (Precio Venta - Costo) / Precio Venta
- ✅ Valor de Inventario por Tienda
- ✅ Rentabilidad por Centro de Costo
- ✅ Flujo de Caja Operativo

---

## 📂 Archivos Relacionados

- [ESTRUCTURA_INVENTARIO_FINANZAS.md](ESTRUCTURA_INVENTARIO_FINANZAS.md) - Documentación detallada
- [GUIA_USO_INVENTARIO_FINANZAS.md](GUIA_USO_INVENTARIO_FINANZAS.md) - Guía de uso
- [RESUMEN_MODELO_COMPLETO.md](RESUMEN_MODELO_COMPLETO.md) - Resumen ejecutivo
- [QUICKSTART_INVENTARIO_FINANZAS.md](QUICKSTART_INVENTARIO_FINANZAS.md) - Guía rápida

---

**Última actualización:** 16 de Diciembre de 2025  
**Versión del Modelo:** 2.0 - Data Warehouse Completo
