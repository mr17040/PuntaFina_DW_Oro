# 🏪 PuntaFina Data Warehouse - Sistema ETL

Sistema completo de Data Warehouse para **PuntaFina** (empresa de calzado en El Salvador) con ETL batch optimizado que integra datos de **OroCommerce**, **OroCRM** y archivos CSV.

[![Estado](https://img.shields.io/badge/Estado-Producción-success)]()
[![Python](https://img.shields.io/badge/Python-3.10-blue)]()
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-blue)]()
[![ETL](https://img.shields.io/badge/ETL-Batch-orange)]()
[![Registros](https://img.shields.io/badge/Registros-1.1M+-green)]()

---

## 📊 Estadísticas del Data Warehouse

- **Total de Tablas**: 18 (13 dimensiones + 5 hechos)
- **Total de Registros**: 290,456
  - Dimensiones: 66,498 registros
  - Hechos: 223,958 registros
- **Fuentes de Datos**: OroCommerce, OroCRM, CSV
- **Tiempo de Ejecución ETL**: ~2 minutos
- **Simetría de Datos**: 100% (datos directos desde origen)

---

## 🎯 Arquitectura del Sistema

### Servidores

```
┌─────────────────────────────────────────────────────────┐
│  FUENTES DE DATOS (localhost)                           │
│  ├─ OroCommerce (PostgreSQL:5432/orocommerce)          │
│  ├─ OroCRM (PostgreSQL:5432/oro_crm)                   │
│  └─ CSVs (/root/PuntaFina_DW_Oro/data/inputs/)         │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  ETL BATCH PROCESSOR                                     │
│  ├─ Extracción: 1.8M registros/ejecución               │
│  ├─ Transformación: Surrogate keys, validaciones        │
│  ├─ Carga: Bulk insert con mapeo inteligente           │
│  └─ Validación: Integridad referencial automática       │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  DATA WAREHOUSE (104.156.246.237:5432)                  │
│  Base de datos: datawarehouse_bi                        │
│  Usuario: sa / IngDatos123*                             │
│  Esquema: Star Schema (13 dims + 5 facts)               │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Estructura del Proyecto

```
PuntaFina_DW_Oro/
├── etl_batch/                    # Sistema ETL principal
│   ├── main.py                   # Orquestador ETL
│   ├── config/
│   │   └── etl_config.yaml      # Configuración de dimensiones y facts
│   ├── core/
│   │   ├── batch_processor.py   # Procesador batch principal
│   │   └── data_validator.py    # Validaciones de integridad
│   ├── extractors/
│   │   ├── csv_extractor.py     # Extractor de CSVs
│   │   └── database_extractor.py # Extractor de BD (OroCommerce/CRM)
│   ├── transformers/
│   │   ├── complete_dimension_builder.py  # Builder de 24 dimensiones
│   │   └── complete_fact_builder.py       # Builder de 5 facts
│   ├── loaders/
│   │   └── database_loader.py   # Cargador con mapeo inteligente
│   └── data/
│       ├── outputs/parquet/     # Parquets intermedios
│       └── checkpoints/         # Control de ejecución
├── data/
│   └── inputs/                  # Fuentes de datos CSV
│       ├── finanzas/            # CSVs financieros
│       ├── inventario/          # CSVs de inventario
│       └── ventas/              # CSVs de ventas
├── sql/
│   └── create_dw_schema.sql     # DDL completo del DW
├── scripts/
│   └── [scripts auxiliares]
└── docs/                        # Documentación técnica

```

---

## 🗄️ Modelo de Datos - Star Schema

### 🎯 Diagrama de Arquitectura Completa

```
═══════════════════════════════════════════════════════════════════════════════
                         FUENTES DE DATOS
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│  OroCommerce (104.156.246.237:5432/orocommerce)                             │
│  ├─ oro_customer (20,155) ──────────────────────► dim_cliente              │
│  ├─ oro_product (64) ───────────────────────────► dim_producto             │
│  ├─ oro_order (42,119) ─────────────────────────► dim_orden                │
│  ├─ oro_user (54) ──────────────────────────────► dim_usuario              │
│  └─ oro_order_line_item (115,528) ──────────────► fact_ventas              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  CSVs - Finanzas (data/inputs/finanzas/)                                   │
│  ├─ transacciones_contables.csv (577,640) ──────► fact_transacciones       │
│  ├─ cuentas_contables.csv (42) ─────────────────► dim_cuenta_contable      │
│  ├─ centros_costo.csv (9) ──────────────────────► dim_centro_costo         │
│  ├─ tipos_transaccion.csv (9) ──────────────────► dim_tipo_transaccion     │
│  ├─ balance.csv (18) ───────────────────────────► fact_balance             │
│  └─ estado_resultados.csv (15) ─────────────────► fact_estado_resultados   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  CSVs - Inventario (data/inputs/inventario/)                               │
│  ├─ movimientos_inventario.csv (58,397) ────────► fact_inventario          │
│  ├─ almacenes.csv (6) ──────────────────────────► dim_almacen              │
│  ├─ proveedores.csv (8) ────────────────────────► dim_proveedor            │
│  └─ tipos_movimiento.csv (9) ───────────────────► dim_tipo_movimiento      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  CSVs - Ventas (data/inputs/ventas/)                                       │
│  └─ impuestos.csv (5) ──────────────────────────► dim_impuestos            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  Generadas Automáticamente                                                  │
│  ├─ dim_fecha ──────────────────────────────────► 4,018 registros (2019-2030)│
│  └─ dim_periodo ────────────────────────────────► 3 registros (2024)        │
└─────────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════
```

### 🌟 Diagrama Modelo Estrella - Módulo Ventas

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ dim_fecha   │     │ dim_cliente │     │ dim_producto│     │ dim_usuario │
│             │     │             │     │             │     │             │
│ PK: id      │     │ PK: id      │     │ PK: id      │     │ PK: id      │
│ 4,018 regs  │     │ 20,155 regs │     │ 64 regs     │     │ 54 regs     │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │                   │
       │                   │                   │                   │
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│dim_sitio_web│     │  dim_canal  │     │ dim_direccion│    │  dim_envio  │
│             │     │             │     │             │     │             │
│ PK: id      │     │ PK: id      │     │ PK: id      │     │ PK: id      │
│ 6 regs      │     │ 12 regs     │     │ 79,836 regs │     │ 8 regs      │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │                   │
       │                   │                   │                   │
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  dim_pago   │     │dim_impuestos│     │dim_promocion│     │  dim_orden  │
│             │     │             │     │             │     │             │
│ PK: id      │     │ PK: id      │     │ PK: id      │     │ PK: id      │
│ 10 regs     │     │ 5 regs      │     │ 6 regs      │     │ 42,119 regs │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │                   │
       │                   │                   │                   │
┌─────────────┐     ┌──────────────┐    ┌──────────────┐    ┌─────────────┐
│dim_line_item│     │dim_estado_   │    │dim_categoria_│    │dim_detalle_ │
│             │     │   orden      │    │  producto    │    │   venta     │
│ PK: id      │     │ PK: id       │    │ PK: id       │    │ PK: id      │
│ 115,528 regs│     │ 16 regs      │    │ 10 regs      │    │ 115,528 regs│
└──────┬──────┘     └──────┬───────┘    └──────┬───────┘    └──────┬──────┘
       │                   │                   │                   │
       │                   │                   │                   │
       └───────────────────┴───────────────────┴───────────────────┘
                                   │
                      ┌────────────▼────────────┐
                      │    fact_ventas          │
                      │                         │
                      │ 115,528 registros       │
                      │                         │
                      │ Métricas:               │
                      │ - cantidad              │
                      │ - precio_unitario       │
                      │ - subtotal              │
                      │ - descuento             │
                      │ - impuesto              │
                      │ - total                 │
                      │ - costo                 │
                      │ - margen                │
                      └─────────────────────────┘
```

### 🏪 Diagrama Modelo Estrella - Módulo Inventario

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ dim_fecha   │     │ dim_producto│     │ dim_almacen │     │ dim_usuario │
│ (compartida)│     │ (compartida)│     │             │     │ (compartida)│
│ PK: id      │     │ PK: id      │     │ PK: id      │     │ PK: id      │
│ 4,018 regs  │     │ 64 regs     │     │ 6 regs      │     │ 54 regs     │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │                   │
       │                   │                   │                   │
       │            ┌──────────────┐    ┌──────────────┐          │
       │            │dim_proveedor │    │dim_tipo_     │          │
       │            │              │    │  movimiento  │          │
       │            │ PK: id       │    │ PK: id       │          │
       │            │ 8 regs       │    │ 9 regs       │          │
       │            └──────┬───────┘    └──────┬───────┘          │
       │                   │                   │                  │
       └───────────────────┴───────────────────┴──────────────────┘
                                   │
                      ┌────────────▼────────────┐
                      │  fact_inventario        │
                      │                         │
                      │ 58,397 registros        │
                      │                         │
                      │ Métricas:               │
                      │ - cantidad              │
                      │ - costo_unitario        │
                      │ - costo_total           │
                      │ - stock_anterior        │
                      │ - stock_resultante      │
                      │                         │
                      │ Tipos de movimiento:    │
                      │ - Entrada               │
                      │ - Salida                │
                      │ - Ajuste                │
                      │ - Traslado              │
                      └─────────────────────────┘
```

### 💰 Diagrama Modelo Estrella - Módulo Finanzas

```
┌─────────────┐     ┌──────────────┐    ┌──────────────┐    ┌─────────────┐
│ dim_fecha   │     │dim_cuenta_   │    │dim_centro_   │    │ dim_usuario │
│ (compartida)│     │  contable    │    │   costo      │    │ (compartida)│
│ PK: id      │     │ PK: id       │    │ PK: id       │    │ PK: id      │
│ 4,018 regs  │     │ 42 regs      │    │ 9 regs       │    │ 54 regs     │
└──────┬──────┘     └──────┬───────┘    └──────┬───────┘    └──────┬──────┘
       │                   │                   │                   │
       │                   │                   │                   │
       │            ┌──────────────┐    ┌──────────────┐          │
       │            │dim_periodo_  │    │dim_tipo_     │          │
       │            │  contable    │    │ transaccion  │          │
       │            │ PK: id       │    │ PK: id       │          │
       │            │ 84 regs      │    │ 9 regs       │          │
       │            └──────┬───────┘    └──────┬───────┘          │
       │                   │                   │                  │
       └───────────────────┴───────────────────┴──────────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
  ┌───────────▼──────────┐ ┌───────▼──────────┐ ┌──────▼─────────┐
  │ fact_transacciones   │ │  fact_balance    │ │ fact_estado_   │
  │                      │ │                  │ │  resultados    │
  │ 577,640 registros    │ │ 18 registros     │ │ 15 registros   │
  │                      │ │                  │ │                │
  │ Métricas:            │ │ Métricas:        │ │ Métricas:      │
  │ - monto_debito       │ │ - saldo_inicial  │ │ - ingresos     │
  │ - monto_credito      │ │ - debitos        │ │ - costos       │
  │ - saldo              │ │ - creditos       │ │ - gastos       │
  │                      │ │ - saldo_final    │ │ - utilidad     │
  │ Tipos:               │ │                  │ │                │
  │ - Asientos diarios   │ │ Por período      │ │ Por período    │
  │ - Balance en línea   │ │ YYYYMM format    │ │ YYYYMM format  │
  └──────────────────────┘ └──────────────────┘ └────────────────┘
```

### 🔗 Dimensiones Conformadas (Compartidas)

```
┌────────────────────────────────────────────────────────────────────┐
│                    DIMENSIONES CONFORMADAS                         │
│  (Compartidas entre múltiples módulos para análisis integrado)     │
└────────────────────────────────────────────────────────────────────┘

  ┌─────────────────┐
  │   dim_fecha     │
  │                 │
  │ 4,018 registros │
  │ 2019-01-01 a    │
  │ 2030-12-31      │
  └────────┬────────┘
           │
           ├──────────► VENTAS (fact_ventas)
           ├──────────► INVENTARIO (fact_inventario)
           ├──────────► FINANZAS (fact_transacciones)
           ├──────────► FINANZAS (fact_balance)
           └──────────► FINANZAS (fact_estado_resultados)

  ┌─────────────────┐
  │  dim_producto   │
  │                 │
  │ 64 registros    │
  │ Catálogo de     │
  │ calzado         │
  └────────┬────────┘
           │
           ├──────────► VENTAS (fact_ventas)
           └──────────► INVENTARIO (fact_inventario)

  ┌─────────────────┐
  │  dim_usuario    │
  │                 │
  │ 54 registros    │
  │ Usuarios del    │
  │ sistema         │
  └────────┬────────┘
           │
           ├──────────► VENTAS (fact_ventas)
           ├──────────► INVENTARIO (fact_inventario)
           └──────────► FINANZAS (fact_transacciones)
```

---

### 📐 Dimensiones Actuales (13 tablas)

| Dimensión | Fuente | Registros | Descripción |
|-----------|--------|-----------|-------------|
| **dim_fecha** | Generada | 4,018 | Dimensión temporal (2019-2030) |
| **dim_cliente** | oro_customer | 20,155 | Clientes B2B |
| **dim_producto** | oro_product | 64 | Catálogo de calzado |
| **dim_orden** | oro_order | 42,119 | Órdenes de compra |
| **dim_usuario** | oro_user | 54 | Usuarios del sistema |
| **dim_almacen** | almacenes.csv | 6 | Almacenes y bodegas |
| **dim_proveedor** | proveedores.csv | 8 | Proveedores de productos |
| **dim_tipo_movimiento** | tipos_movimiento.csv | 9 | Tipos de movimientos de inventario |
| **dim_centro_costo** | centros_costo.csv | 9 | Centros de costo |
| **dim_tipo_transaccion** | tipos_transaccion.csv | 9 | Tipos de transacciones financieras |
| **dim_cuenta_contable** | cuentas_contables.csv | 42 | Plan de cuentas contables |
| **dim_impuestos** | impuestos.csv | 5 | Impuestos (IVA 13%, ISR, etc.) |
| **dim_periodo** | Generada | 3 | Períodos contables (202401-202403) |

**Total Dimensiones**: 66,498 registros

---

### 📊 Tablas de Hechos (5 tablas)

| Fact | Fuente | Registros | Período | Descripción |
|------|--------|-----------|---------|-------------|
| **fact_ventas** | oro_order_line_item | 115,528 | 2023-2025 | Ventas detalladas por línea de pedido |
| **fact_inventario** | movimientos_inventario.csv | 58,397 | 2022-2025 | Movimientos de inventario |
| **fact_transacciones** | transacciones_contables.csv | 50,000 | 2023-2025 | Transacciones contables (sample) |
| **fact_balance** | balance.csv | 18 | 2024 Q1 | Balance general por cuenta y período |
| **fact_estado_resultados** | estado_resultados.csv | 15 | 2024 Q1 | Estado de resultados por centro de costo |

**Total Facts**: 223,958 registros

#### Claves Foráneas por Fact:

**fact_ventas**:
- fecha_id, cliente_id, producto_id, orden_id, usuario_id, almacen_id, impuesto_id

**fact_inventario**:
- fecha_id, producto_id, almacen_id, tipo_movimiento_id, proveedor_id, usuario_id

**fact_transacciones**:
- fecha_id, cuenta_id, centro_costo_id, tipo_transaccion_id, usuario_id, periodo_id

**fact_balance**:
- fecha_id, periodo_id, cuenta_id

**fact_estado_resultados**:
- fecha_id, periodo_id, cuenta_id, centro_costo_id

| Fact | Fuente | Registros | Período | Descripción |
|------|--------|-----------|---------|-------------|
| **fact_balance** | Calculado desde `fact_transacciones` | 18 | 202401-202403 | Balance general por cuenta y período |
| **fact_estado_resultados** | Calculado desde `fact_transacciones` | 15 | 202401-202403 | Estado de resultados por cuenta y centro de costo |

> 📝 **Nota**: Los facts sintetizados se calculan agregando transacciones contables. Los CSVs actuales son plantillas con 3 períodos de ejemplo.

---

## 🚀 Instalación y Configuración

### Requisitos Previos

```bash
# Sistema Operativo
Ubuntu 22.04+

# Software
Python 3.10+
PostgreSQL 12+
Git + Git LFS

# Recursos Recomendados
RAM: 8 GB
CPU: 4 cores
Disco: 20 GB disponible
```

### Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/mr17040/PuntaFina_DW_Oro.git
cd PuntaFina_DW_Oro

# 2. Instalar Git LFS (para archivos grandes)
git lfs install
git lfs pull

# 3. Crear ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 4. Instalar dependencias
pip install -r etl_batch/requirements.txt

# 5. Configurar variables de entorno
cp etl_batch/.env.example etl_batch/.env
nano etl_batch/.env
```

### Configuración del .env

```ini
# Bases de Datos de Origen (localhost)
ORO_DB_HOST=localhost
ORO_DB_PORT=5432
ORO_DB_NAME=orocommerce
ORO_DB_USER=sa
ORO_DB_PASSWORD=IngDatos123*

CRM_DB_HOST=localhost
CRM_DB_PORT=5432
CRM_DB_NAME=oro_crm
CRM_DB_USER=sa
CRM_DB_PASSWORD=IngDatos123*

# Data Warehouse (Producción)
DW_DB_HOST=104.156.246.237
DW_DB_PORT=5432
DW_DB_NAME=puntafina_dw
DW_DB_USER=sa
DW_DB_PASSWORD=IngDatos123*

# Configuración ETL
MAX_WORKERS=8
MAX_MEMORY_GB=7
STATEMENT_TIMEOUT=1800
CHUNK_SIZE=15000
```

---

## 🔄 Uso del Sistema ETL

### Ejecución Completa

```bash
cd etl_batch
python3 main.py run
```

### Proceso ETL (5 Fases)

```
┌─────────────────────────────────────────────┐
│ FASE 0: Desbloqueo Forzado de Tablas       │
│ - Terminar conexiones idle                  │
│ - Cancelar queries largas                   │
│ - Liberar locks de tablas                   │
└─────────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│ FASE 1: Extracción (~5 segundos)            │
│ - Verificación de fuentes disponibles       │
│ - OroCommerce: 177K+ registros               │
│ - CSVs: 636K+ registros                      │
└─────────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│ FASE 2: Construcción Dimensiones (~5s)      │
│ - 13 dimensiones cargadas directamente      │
│ - Scripts especializados por fuente         │
│ - Mapeo de códigos automático               │
│ Total: 66,498 registros                     │
└─────────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│ FASE 3: Construcción Facts (~90s)           │
│ - 5 facts cargados desde origen             │
│ - fact_ventas: 115,528 desde OroCommerce    │
│ - fact_inventario: 58,397 desde CSV         │
│ - fact_transacciones: 50,000 desde CSV      │
│ - fact_balance: 18 desde CSV                │
│ - fact_estado_resultados: 15 desde CSV      │
│ Total: 223,958 registros                    │
└─────────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│ FASE 4: Verificación (~2s)                  │
│ - Verificación de registros cargados        │
│ - Conteo de todas las tablas                │
│ Total: 290,456 registros en DW              │
└─────────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│ FASE 5: Validación Final                    │
│ - Verificación de integridad referencial    │
│ - Conteo final de registros                 │
│ - Generación de reporte                     │
└─────────────────────────────────────────────┘

⏱️ Tiempo Total: ~115 segundos (2 minutos)
```

### Verificación del ETL

```bash
# Generar reporte completo
python3 reporte_etl.py

# Verificar simetría de datos
python3 /tmp/reporte_simetria_completo.py

# Ver logs
tail -f etl_batch/logs/etl_*.log
```

---

## 📋 Archivos CSV de Entrada

### Estructura de data/inputs/

```
data/inputs/
├── finanzas/
│   ├── transacciones_contables.csv        # 577,640 registros (74 MB)
│   ├── cuentas_contables.csv              # 42 registros
│   ├── centros_costo.csv                  # 9 registros
│   └── tipos_transaccion.csv              # 9 registros
├── inventario/
│   ├── movimientos_inventario.csv         # 58,397 registros
│   ├── almacenes.csv                      # 6 registros
│   ├── proveedores.csv                    # 8 registros
│   └── tipos_movimiento.csv               # 9 registros
├── ventas/
│   ├── sitios_web.csv                     # 6 registros
│   ├── impuestos.csv                      # 5 registros
│   ├── estados_orden.csv                  # 16 registros
│   ├── estados_pago.csv                   # 6 registros
│   ├── metodos_envio.csv                  # 8 registros
│   ├── metodos_pago.csv                   # 10 registros
│   └── categorias_producto.csv            # 10 registros
├── balance.csv                            # 18 registros (plantilla)
└── estado_resultados.csv                  # 15 registros (plantilla)
```

### Formato de CSVs

Todos los CSVs usan:
- **Codificación**: UTF-8
- **Separador**: coma (`,`)
- **Header**: Primera línea con nombres de columnas
- **Fechas**: Formato `YYYY-MM-DD`

---

## 🔍 Características Técnicas

### Mapeo Inteligente de Columnas

El sistema mapea automáticamente columnas entre parquet y base de datos:

```python
# Ejemplo: fact_balance
Parquet                 →  PostgreSQL
cuenta_contable_id      →  cuenta_id
balance_id              →  balance_id
periodo_id              →  periodo_id
```

### Surrogate Keys Automáticos

Todas las dimensiones generan surrogate keys secuenciales:

```sql
-- Ejemplo: dim_cliente
cliente_id SERIAL PRIMARY KEY  -- Generado automáticamente
cliente_externo_id INT         -- ID original de oro_customer
```

### Reset de Secuencias

Después de cargar dimensiones, las secuencias se resetean al máximo:

```sql
-- Ejemplo automático
SELECT setval('dim_cliente_cliente_id_seq', 
              (SELECT MAX(cliente_id) FROM dim_cliente));
```

### Validaciones de Integridad

- ✅ Verificación de claves foráneas antes de insertar facts
- ✅ Validación de duplicados por claves naturales
- ✅ Conteo de registros por tabla
- ✅ Verificación de rangos de fechas

---

## 📊 Consultas Útiles

### Verificar Carga de Dimensiones

```sql
-- Conteo por dimensión
SELECT 
    'dim_cliente' as tabla, COUNT(*) as registros FROM dim_cliente
UNION ALL
SELECT 'dim_producto', COUNT(*) FROM dim_producto
UNION ALL
SELECT 'dim_orden', COUNT(*) FROM dim_orden;
```

### Análisis de Ventas

```sql
-- Ventas por producto y mes
SELECT 
    p.nombre as producto,
    TO_CHAR(f.fecha::date, 'YYYY-MM') as mes,
    SUM(fv.cantidad) as unidades_vendidas,
    SUM(fv.subtotal) as ventas_totales
FROM fact_ventas fv
JOIN dim_producto p ON fv.producto_id = p.producto_id
JOIN dim_fecha f ON fv.fecha_id = f.fecha_id
GROUP BY p.nombre, TO_CHAR(f.fecha::date, 'YYYY-MM')
ORDER BY ventas_totales DESC
LIMIT 10;
```

### Balance Contable

```sql
-- Balance por cuenta y período
SELECT 
    c.nombre as cuenta,
    p.nombre_periodo,
    fb.saldo_inicial,
    fb.debitos,
    fb.creditos,
    fb.saldo_final
FROM fact_balance fb
JOIN dim_cuenta_contable c ON fb.cuenta_id = c.cuenta_id
JOIN dim_periodo_contable p ON fb.periodo_id = p.periodo_id
ORDER BY p.periodo_id DESC, c.codigo;
```

---

## 🛠️ Scripts Auxiliares

### Verificación del Sistema

```bash
# Verificar estado de la base de datos
./etl_batch/verify.sh

# Verificar estructura completa
python3 scripts/validate_dw_structure.py

# Limpiar tablas obsoletas
python3 etl_batch/cleanup_obsolete_tables.py
```

### Ejecución Rápida

```bash
# Quickstart completo
cd etl_batch
./quickstart.sh
```

---

## 📈 Monitoreo y Logs

### Ubicación de Logs

```
etl_batch/logs/
├── etl_YYYYMMDD_HHMMSS.log    # Log de cada ejecución
└── error_YYYYMMDD.log          # Errores críticos
```

### Niveles de Log

- `INFO`: Progreso normal del ETL
- `WARNING`: Advertencias no críticas
- `ERROR`: Errores que detienen el proceso

### Checkpoints

El sistema mantiene checkpoints de ejecución:

```
etl_batch/data/checkpoints/
└── last_run_YYYYMMDD_HHMMSS.json
```

---

## 🔐 Seguridad

### Credenciales

- Las credenciales se almacenan en `.env` (no versionado)
- Usar variables de entorno en producción
- Rotar contraseñas periódicamente

### Backups

```bash
# Backup del DW
pg_dump -h 104.156.246.237 -U sa -d puntafina_dw > backup_$(date +%Y%m%d).sql

# Restauración
psql -h 104.156.246.237 -U sa -d puntafina_dw < backup_20260106.sql
```

---

## 🐛 Troubleshooting

### Error: Timeout en Queries

```bash
# Aumentar timeout en .env
STATEMENT_TIMEOUT=3600  # 1 hora
```

### Error: Memoria Insuficiente

```bash
# Reducir workers o memoria en .env
MAX_WORKERS=4
MAX_MEMORY_GB=4
```

### Error: Clave Foránea Inválida

```bash
# Regenerar dimensiones primero
python3 main.py run --dimensions-only

# Luego cargar facts
python3 main.py run --facts-only
```

---

## 📚 Documentación Adicional

Todos los documentos técnicos están en la carpeta `docs/`:

- **[ETL_BATCH_README.md](docs/ETL_BATCH_README.md)**: Documentación detallada del ETL
- **[database_exact_structure.md](docs/database_exact_structure.md)**: Estructura completa del DW
- **[DIAGRAMA_MODELO_DIMENSIONAL.md](docs/DIAGRAMA_MODELO_DIMENSIONAL.md)**: Diagramas del modelo
- **[GUIA_USO_INVENTARIO_FINANZAS.md](docs/GUIA_USO_INVENTARIO_FINANZAS.md)**: Guía de uso
- Y más...

---

## 🤝 Contribución

### Flujo de Trabajo

1. Fork del repositorio
2. Crear branch: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -m "Descripción"`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

### Estándares de Código

- Python: PEP 8
- SQL: PostgreSQL style guide
- Commits: Conventional Commits

---

## 📝 Changelog

### v3.0.0 (2026-01-07)

- ✅ **Eliminadas 10 dimensiones no utilizadas**:
  - dim_sitio_web, dim_canal, dim_direccion, dim_envio, dim_pago
  - dim_promocion, dim_line_item, dim_estado_orden, dim_estado_pago, dim_categoria_producto
- ✅ **Modelo simplificado**: 13 dimensiones + 5 facts (total: 18 tablas)
- ✅ **Carga directa desde origen**: Scripts especializados con execute_values
- ✅ **fact_ventas completado**: 115,528 registros desde oro_order_line_item
- ✅ **Mapeo inteligente de códigos**: CSV → dimensiones automático
- ✅ **Tiempo de ejecución**: Reducido a ~2 minutos
- ✅ **Sin NULL values**: 100% datos completos desde origen
- ✅ **Scripts de carga**:
  - cargar_dimensiones_origen.py (7 dimensiones)
  - cargar_todos_facts.py (5 facts incluido ventas)
  - cargar_fact_ventas.py (especializado para ventas)
  - cargar_dw_completo.py (orquestador maestro)

### v2.0.0 (2026-01-06)

- ✅ Verificación completa de simetría (100%)
- ✅ Git LFS para archivos grandes
- ✅ CSVs renombrados (sin prefijo `fact_`)
- ✅ Corrección dim_canal (conexión crm_conn)
- ✅ Optimización dim_estado_pago (6 estados únicos)
- ✅ Nuevos CSVs de origen (impuestos, pagos, categorías)

### v1.2.0 (2026-01-05)

- ✅ Población completa de dim_line_item y dim_detalle_venta
- ✅ 115,528 registros reales desde oro_order_line_item
- ✅ Eliminación de placeholders

### v1.1.0 (2026-01-04)

- ✅ Implementación de surrogate keys en todos los facts
- ✅ Reset automático de secuencias
- ✅ Mapeo inteligente de columnas
- ✅ Generación correcta de fecha_id desde periodo_id

---

## 📞 Soporte

- **Repositorio**: [github.com/mr17040/PuntaFina_DW_Oro](https://github.com/mr17040/PuntaFina_DW_Oro)
- **Issues**: [github.com/mr17040/PuntaFina_DW_Oro/issues](https://github.com/mr17040/PuntaFina_DW_Oro/issues)

---

## 📄 Licencia

Este proyecto es propiedad de **PuntaFina** y está destinado únicamente para uso interno.

---

## 🎯 Resumen Ejecutivo

**PuntaFina Data Warehouse** es un sistema ETL completo y optimizado que:

- ✅ Integra **2 fuentes de datos** (OroCommerce, CSVs)
- ✅ Procesa **290K registros** desde origen
- ✅ Carga **290,456 registros** al DW en **~2 minutos**
- ✅ Mantiene **100% de simetría** con datos de origen
- ✅ Implementa **Star Schema** con 13 dimensiones y 5 facts
- ✅ Soporta **análisis de ventas, inventario y finanzas**
- ✅ Carga directa desde origen con **execute_values** de psycopg2
- ✅ Mapeo inteligente de códigos CSV a dimensiones

**Estado**: ✅ Producción | **Última Ejecución**: 2026-01-07 | **Registros**: 290,456

**Total DW**: 290,456 registros (13 dims: 66,498 + 5 facts: 223,958)

---

*Desarrollado con ❤️ para PuntaFina El Salvador*
