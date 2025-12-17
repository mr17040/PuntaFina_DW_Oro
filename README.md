# 🏪 Data Warehouse PuntaFina - Solución Analítica Completa

## 📊 Descripción General

Sistema integral de Data Warehouse para **PuntaFina**, empresa de venta de calzado con **5 tiendas físicas + 1 tienda en línea**. Implementa un modelo dimensional completo que integra datos de **Ventas, Inventario y Finanzas** desde **OroCRM y OroCommerce**.

### ✨ Versión 2.0 - Actualización Mayor
- ✅ Módulo de Ventas (original)
- 🆕 Módulo de Inventario (nuevo)
- 🆕 Módulo de Finanzas (nuevo)
- 🆕 Integración completa entre módulos

## 🎯 Objetivos del Negocio

### Necesidades Identificadas
- ❌ **Problema:** Los sistemas actuales (OroCRM/OroCommerce) no tienen reportes predefinidos
- ❌ **Proceso actual:** Descarga de datos a Excel para análisis manual
- ✅ **Solución:** Data Warehouse automatizado con reportes en tiempo real

### Decisiones Clave a Soportar
1. ✅ Ventas diarias, mensuales y anuales
2. ✅ Niveles de inventario diario y mensual
3. ✅ Productos más vendidos
4. ✅ Clientes más importantes
5. ✅ Estado de resultados y balance general
6. ✅ Costos de inventarios

### KPIs Principales
- 📊 **Costo promedio de inventario mensual**
- 📈 **Cumplimiento de meta de venta mensual**
- 💰 **Margen bruto**
- 💵 **Margen neto**

## 🏗️ Arquitectura

### Modelo Dimensional
**Esquema Estrella ampliado:** 19 dimensiones + 5 tablas de hechos

```
        VENTAS (13 dim + 1 fact)
              ↓
        fact_ventas
              ↓
              ├──► INVENTARIO (3 dim + 1 fact)
              │         ↓
              │    fact_inventario
              │
              └──► FINANZAS (3 dim + 3 facts)
                        ↓
                  fact_transacciones_contables
                  fact_estado_resultados
                  fact_balance_general
```

## 🚀 Inicio Rápido

### Requisitos Previos
- Python 3.8+
- PostgreSQL 12+
- Acceso a bases de datos OroCRM/OroCommerce
- 8GB RAM mínimo

### Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <repo-url>
   cd PuntaFina_DW_Oro-main
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar credenciales**
   - Copiar `config/.env.example` a `config/.env`
   - Completar credenciales de bases de datos

4. **Completar archivos CSV** (🆕 NUEVO)
   - `data/inputs/inventario/*.csv` - Datos de inventario
   - `data/inputs/finanzas/*.csv` - Datos financieros
   - Ver [GUIA_USO_INVENTARIO_FINANZAS.md](docs/GUIA_USO_INVENTARIO_FINANZAS.md)

5. **Ejecutar el ETL completo**
   ```bash
   cd scripts
   python orquestador_maestro.py
   ```

### 📖 Documentación Rápida

| Documento | Descripción |
|-----------|-------------|
| [QUICKSTART_INVENTARIO_FINANZAS.md](QUICKSTART_INVENTARIO_FINANZAS.md) | 🚀 Inicio rápido para nuevos módulos |
| [GUIA_USO_INVENTARIO_FINANZAS.md](docs/GUIA_USO_INVENTARIO_FINANZAS.md) | 📖 Guía completa de uso de CSV |
| [CATALOGO_ESTADOS_VENTAS.md](docs/CATALOGO_ESTADOS_VENTAS.md) | 📋 Estados de órdenes, pagos y envíos |
| [RESUMEN_MODELO_COMPLETO.md](docs/RESUMEN_MODELO_COMPLETO.md) | 📊 Resumen ejecutivo del modelo |
| [DIAGRAMA_MODELO_DIMENSIONAL.md](docs/DIAGRAMA_MODELO_DIMENSIONAL.md) | 🗺️ Diagrama visual del modelo |
| [IMPLEMENTACION_COMPLETADA.md](IMPLEMENTACION_COMPLETADA.md) | ✅ Resumen de implementación |

---

## 📦 Componentes Principales

### Scripts del Pipeline ETL

#### 1. `build_all_dimensions.py` (Ventas)
Construye 13 dimensiones del módulo de ventas desde OroCommerce:
- dim_fecha, dim_cliente, dim_producto, dim_usuario
- dim_sitio_web, dim_canal, dim_direccion, dim_envio
- dim_pago, dim_impuestos, dim_promocion, dim_orden, dim_line_item

#### 2. `build_fact_ventas.py` (Ventas)
Tabla de hechos principal con transacciones de venta:
- ~30,000 registros (líneas de pedido)
- 26 campos incluyendo métricas y foreign keys
- Cálculos de descuentos y stock dinámico

#### 3. 🆕 `build_inventario_finanzas.py` (Inventario + Finanzas)
Construye 6 dimensiones y 4 tablas de hechos:

**Dimensiones:**
- dim_proveedor, dim_almacen, dim_movimiento_tipo
- dim_cuenta_contable, dim_centro_costo, dim_tipo_transaccion

**Hechos:**
- fact_inventario (~100K movimientos)
- fact_transacciones_contables (~200K asientos)
- fact_estado_resultados (agregado mensual)
- fact_balance_general (saldos a fecha)

#### 4. `setup_database.py`
- Crea base de datos PostgreSQL si no existe
- Crea las 24 tablas (19 dim + 5 facts)
- Establece foreign keys e índices
- Carga datos desde archivos parquet

#### 5. `orquestador_maestro.py`
Pipeline completo en secuencia:
1. Dimensiones de Ventas
2. Fact de Ventas
3. 🆕 Dimensiones y Facts de Inventario/Finanzas
4. Setup de base de datos

---

## 📊 Modelo de Datos

### Tablas de Hechos (5)

| Tabla | Registros | Grano | Módulo |
|-------|-----------|-------|--------|
| `fact_ventas` | ~30K | Línea de pedido | Ventas |
| `fact_inventario` | ~100K | Movimiento de inventario | 🆕 Inventario |
| `fact_transacciones_contables` | ~200K | Línea de asiento | 🆕 Finanzas |
| `fact_estado_resultados` | ~1K | Mes + Cuenta | 🆕 Finanzas |
| `fact_balance_general` | ~2K | Fecha + Cuenta | 🆕 Finanzas |

### Dimensiones (19)

#### Módulo Ventas (13)
- dim_fecha, dim_cliente, dim_producto, dim_usuario
- dim_sitio_web, dim_canal, dim_direccion, dim_envio
- dim_pago, dim_impuestos, dim_promocion
- dim_orden, dim_line_item

#### 🆕 Módulo Inventario (3 propias + 3 compartidas)
**Dimensiones Propias:**
- dim_proveedor - Proveedores de calzado
- dim_almacen - Almacenes y tiendas
- dim_movimiento_tipo - Tipos de movimiento

**Dimensiones Compartidas:**
- 🔗 dim_producto (del módulo Ventas)
- 🔗 dim_usuario (del módulo Ventas)

**Dimensiones Compartidas:**
- 🔗 dim_usuario (del módulo Ventas)
- 🔗 dim_fecha (del módulo Ventas)
- 🔗 dim_fecha (del módulo Ventas)

#### 🆕 Módulo Finanzas (3 propias + 2 compartidas)
**Dimensiones Propias:**
- dim_cuenta_contable - Plan de cuentas
- dim_centro_costo - Centros de costo
- dim_tipo_transaccion - Tipos de transacción

---
**Integración mediante dim_producto compartida:**
```sql
-- Costo de productos vendidos
SELECT 
    v.id_producto,
    p.nombre as producto,  -- desde dim_producto compartida
    SUM(v.cantidad) as unidades_vendidas,
    AVG(i.costo_unitario) as costo_promedio,
    SUM(v.cantidad * i.costo_unitario) as costo_total,
    SUM(v.total_linea_neto) as ingresos,
    SUM(v.total_linea_neto) - SUM(v.cantidad * i.costo_unitario) as utilidad_bruta
FROM fact_ventas v
JOIN dim_producto p ON v.id_producto = p.id_producto  -- dimensión compartida
JOIN fact_inventario i ON v.id_producto = i.id_producto
WHERE i.id_tipo_movimiento = 'MOV_ENTRADA'
GROUP BY v.id_producto, p.nombreio) as costo_promedio,
    SUM(v.cantidad * i.costo_unitario) as costo_total
FROM fact_ventas v
JOIN fact_inventario i ON v.id_producto = i.id_producto
GROUP BY v.id_producto;
```

### Ventas ↔ Finanzas
```sql
-- Asientos contables desde ventas
SELECT 
    v.id_venta,
    v.total_orden,
    t.numero_asiento,
    t.tipo_movimiento,
    t.monto
FROM fact_ventas v
JOIN fact_transacciones_contables t ON t.id_venta = v.id_venta;
```

### Inventario ↔ Finanzas
```sql
-- Valorización de inventario en balance
SELECT 
    c.nombre_cuenta,
    SUM(i.stock_resultante * i.costo_unitario) as valor_inventario
FROM fact_inventario i
JOIN dim_cuenta_contable c ON c.id_cuenta = '1104'
GROUP BY c.nombre_cuenta;
```

---

## 🎯 KPIs Implementados

### Ventas
- Ventas diarias/mensuales/anuales
- Top productos más vendidos
- Top clientes más importantes
- Ticket promedio

### 🆕 Inventario
- Costo promedio de inventario mensual
- Rotación de inventario
- Días de inventario
- Stock mínimo vs actual

### 🆕 Finanzas
- Margen bruto %
- Margen neto %
- Cumplimiento de meta de ventas
- Razón corriente

---

## 💾 Características de la Base de Datos

### Integridad Referencial
- 19 dimensiones con primary keys
- 5 tablas de hechos con múltiples foreign keys
- Validaciones automáticas de integridad

### Carga Incremental
- Modo de carga completa e incremental
- ON CONFLICT para upserts eficientes
- Preservación de datos históricos

### Optimización de Rendimiento
Incluye 11 índices estratégicos en campos consultados comúnmente y relaciones de llaves foráneas. El rendimiento de consultas está optimizado para patrones típicos de acceso de inteligencia de negocios.

## Instalación y Configuración

### Prerrequisitos

- Python 3.7 o superior
- PostgreSQL 12 o superior
- Paquetes de Python requeridos: pandas, psycopg2, pyarrow, python-dotenv, pyyaml

### Configuración

Crear un archivo de configuración en `config/.env` con los parámetros de conexión de base de datos:

```
# Source OroCommerce Database
ORO_DB_HOST=your_oro_host
ORO_DB_PORT=5432
ORO_DB_NAME=oro_database
ORO_DB_USER=oro_user
ORO_DB_PASS=oro_password

# Target Data Warehouse Database  
DW_ORO_DB_HOST=your_dw_host
DW_ORO_DB_PORT=5432
DW_ORO_DB_NAME=DW_oro
DW_ORO_DB_USER=dw_user
DW_ORO_DB_PASS=dw_password
```

### Ejecución

Ejecutar el pipeline ETL completo:

```bash
cd scripts
python orquestador_maestro.py
```

Para componentes individuales:

```bash
python build_all_dimensions.py
python build_fact_ventas.py
python setup_database.py
```

## Volumen de Datos y Rendimiento

El sistema procesa aproximadamente 2.8 millones de registros a través de todas las tablas con las siguientes características de rendimiento:

- Construcción de dimensiones: 60-90 segundos
- Construcción de tabla de hechos: 45-60 segundos  
- Carga de base de datos: 120-180 segundos
- Ejecución total del pipeline: 4-5 minutos

## Métricas de Negocio

El data warehouse habilita análisis de:

- Volumen de ventas: $736 millones en valor de transacciones
- Comportamiento del cliente: 437,000+ clientes únicos
- Rendimiento de productos: Analítica detallada a nivel SKU
- Análisis geográfico: Datos completos a nivel de dirección
- Efectividad promocional: Medición de impacto de descuentos
- Tendencias temporales: Historial de transacciones multi-año

## Estructura de Archivos

```
PuntaFina_DW_Oro/
├── scripts/                 # Scripts del pipeline ETL
├── config/                  # Archivos de configuración
├── data/outputs/           # Archivos Parquet y CSV generados
├── docs/                   # Documentación y diccionario de datos
├── logs/                   # Logs de ejecución
└── sql/                    # Consultas SQL de referencia
```

## Registro y Monitoreo

Todas las ejecuciones del pipeline generan logs detallados en el directorio `logs/`. Los archivos de log incluyen timestamps, conteos de registros, métricas de calidad de datos y detalles de errores para resolución de problemas y propósitos de auditoría.

## Mantenimiento

El sistema está diseñado para operación automatizada con requerimientos mínimos de mantenimiento. El enfoque de carga incremental reduce el tiempo de procesamiento para actualizaciones rutinarias mientras preserva el historial de datos para continuidad analítica.
- **15 Foreign Keys** en fact_ventas
- **Índices optimizados** para consultas BI

¡Listo para conectar Power BI, Tableau o cualquier herramienta de análisis!