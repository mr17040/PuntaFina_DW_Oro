# 🏪 PuntaFina Data Warehouse - Sistema ETL

Sistema completo de Data Warehouse para **PuntaFina** (empresa de calzado en El Salvador) con ETL batch optimizado que integra datos de **OroCommerce**, **OroCRM** y archivos CSV.

[![Estado](https://img.shields.io/badge/Estado-Producción-success)]()
[![Python](https://img.shields.io/badge/Python-3.10-blue)]()
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-blue)]()
[![ETL](https://img.shields.io/badge/ETL-Batch-orange)]()
[![Registros](https://img.shields.io/badge/Registros-1.1M+-green)]()

---

## 📊 Estadísticas del Data Warehouse

- **Total de Tablas**: 29 (24 dimensiones + 5 hechos)
- **Total de Registros**: 1,129,146
  - Dimensiones: 377,548 registros
  - Hechos: 751,598 registros
- **Fuentes de Datos**: OroCommerce, OroCRM, CSV
- **Tiempo de Ejecución ETL**: ~4 minutos
- **Simetría de Datos**: 100% (25/25 tablas verificadas)

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
│  Base de datos: puntafina_dw                            │
│  Usuario: sa / IngDatos123*                             │
│  Esquema: Star Schema (24 dims + 5 facts)               │
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

### 📐 Dimensiones (24 tablas)

#### **Dimensiones desde Bases de Datos** (9 tablas)

| Dimensión | Fuente | Tabla Origen | Registros | Descripción |
|-----------|--------|--------------|-----------|-------------|
| **dim_cliente** | OroCommerce | `oro_customer` | 20,155 | Clientes B2B |
| **dim_producto** | OroCommerce | `oro_product` | 64 | Catálogo de productos |
| **dim_orden** | OroCommerce | `oro_order` | 42,119 | Órdenes de compra |
| **dim_usuario** | OroCommerce | `oro_user` | 54 | Usuarios del sistema |
| **dim_canal** | OroCRM | `orocrm_channel` | 12 | Canales de venta |
| **dim_line_item** | OroCommerce | `oro_order_line_item` | 115,528 | Líneas de pedido |
| **dim_detalle_venta** | OroCommerce | `oro_order_line_item` | 115,528 | Detalles de venta |
| **dim_direccion** | OroCommerce | `oro_order_address` | 79,836 | Direcciones de envío |
| **dim_promocion** | OroCommerce | `oro_promotion` | 6 | Promociones activas |

#### **Dimensiones desde CSVs** (13 tablas)

| Dimensión | Archivo CSV | Registros | Descripción |
|-----------|-------------|-----------|-------------|
| **dim_almacen** | `inventario/almacenes.csv` | 6 | Almacenes y bodegas |
| **dim_proveedor** | `inventario/proveedores.csv` | 8 | Proveedores de productos |
| **dim_tipo_movimiento** | `inventario/tipos_movimiento.csv` | 9 | Tipos de movimientos de inventario |
| **dim_cuenta_contable** | `finanzas/cuentas_contables.csv` | 42 | Plan de cuentas contables |
| **dim_centro_costo** | `finanzas/centros_costo.csv` | 9 | Centros de costo |
| **dim_tipo_transaccion** | `finanzas/tipos_transaccion.csv` | 9 | Tipos de transacciones financieras |
| **dim_sitio_web** | `ventas/sitios_web.csv` | 6 | Sitios web y tiendas físicas |
| **dim_impuestos** | `ventas/impuestos.csv` | 5 | Impuestos de El Salvador (IVA 13%, ISR, etc.) |
| **dim_estado_orden** | `ventas/estados_orden.csv` | 16 | Estados del ciclo de vida de orden |
| **dim_estado_pago** | `ventas/estados_pago.csv` | 6 | Estados de pago (pending, paid, etc.) |
| **dim_envio** | `ventas/metodos_envio.csv` | 8 | Métodos de envío |
| **dim_pago** | `ventas/metodos_pago.csv` | 10 | Métodos de pago |
| **dim_categoria_producto** | `ventas/categorias_producto.csv` | 10 | Categorías de calzado |

#### **Dimensiones Generadas** (2 tablas)

| Dimensión | Generación | Registros | Rango |
|-----------|------------|-----------|-------|
| **dim_fecha** | Automática | 4,018 | 2019-01-01 a 2030-12-31 |
| **dim_periodo_contable** | Automática | 84 | 201901 a 202612 (YYYYMM) |

---

### 📊 Tablas de Hechos (5 tablas)

#### **Facts desde Bases de Datos** (1 tabla)

| Fact | Fuente | Tabla Origen | Registros | Período |
|------|--------|--------------|-----------|---------|
| **fact_ventas** | OroCommerce | `oro_order_line_item` | 115,528 | 2023-01-01 a 2025-11-30 |

**Granularidad**: 1 registro = 1 línea de pedido  
**Claves Foráneas**: fecha_id, cliente_id, producto_id, orden_id, direccion_id, usuario_id, canal_id, impuesto_id, estado_orden_id, estado_pago_id, pago_id, envio_id, promocion_id, line_item_id, detalle_id, sitio_id, categoria_id

#### **Facts desde CSVs** (2 tablas)

| Fact | Archivo CSV | Registros | Período |
|------|-------------|-----------|---------|
| **fact_transacciones** | `finanzas/transacciones_contables.csv` | 577,640 | 2023-01-01 a 2025-11-30 |
| **fact_inventario** | `inventario/movimientos_inventario.csv` | 58,397 | 2022-12-15 a 2025-11-30 |

**fact_transacciones** - Granularidad: 1 registro = 1 asiento contable  
**fact_inventario** - Granularidad: 1 registro = 1 movimiento de inventario

#### **Facts Sintetizados** (2 tablas)

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
│ FASE 1: Extracción (~30 segundos)           │
│ - OroCommerce: 1,197,422 registros          │
│ - OroCRM: 12 registros                      │
│ - CSVs: 636,156 registros                   │
│ Total: 1,833,590 registros                  │
└─────────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│ FASE 2: Transformación - Dimensiones (~15s) │
│ - 24 dimensiones construidas                │
│ - Surrogate keys asignados                  │
│ - Validaciones de calidad                   │
│ Total: 377,548 registros                    │
└─────────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│ FASE 3: Transformación - Facts (~35s)       │
│ - 5 facts construidos                       │
│ - Mapeo de FKs a surrogate keys             │
│ - Cálculo de métricas                       │
│ Total: 751,598 registros                    │
└─────────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│ FASE 4: Carga (~170 segundos)               │
│ - Limpieza de facts (TRUNCATE)              │
│ - Carga de dimensiones con upsert           │
│ - Carga de facts con bulk insert            │
│ - Reset de secuencias                       │
│ Total: 1,129,146 registros cargados         │
└─────────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│ FASE 5: Validación                          │
│ - Verificación de integridad referencial    │
│ - Conteo de registros                       │
│ - Generación de reporte                     │
└─────────────────────────────────────────────┘

⏱️ Tiempo Total: ~250 segundos (4 minutos)
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

- ✅ Integra **3 fuentes de datos** (OroCommerce, OroCRM, CSVs)
- ✅ Procesa **1.8 millones de registros** por ejecución
- ✅ Carga **1.1 millones de registros** al DW en **~4 minutos**
- ✅ Mantiene **100% de simetría** con datos de origen
- ✅ Usa **Git LFS** para archivos grandes (228 MB total)
- ✅ Implementa **Star Schema** con 24 dimensiones y 5 facts
- ✅ Soporta **análisis de ventas, inventario y finanzas**

**Estado**: ✅ Producción | **Última Ejecución**: 2026-01-06 05:01 | **Registros**: 1,129,146

---

*Desarrollado con ❤️ para PuntaFina El Salvador*
