# 🏪 PuntaFina ETL Batch System
## Sistema de ETL Optimizado para Procesamiento por Lotes

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Ubuntu](https://img.shields.io/badge/ubuntu-22.04-orange.svg)](https://ubuntu.com/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-12+-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 📋 Descripción

Sistema ETL (Extract, Transform, Load) de última generación diseñado para **PuntaFina**, optimizado para procesamiento por lotes en Ubuntu 22.04. Integra datos de **OroCommerce**, **OroCRM** y archivos **CSV** en un Data Warehouse dimensional con validación automática y población inteligente de datos.

### ✨ Características Principales

- ✅ **Procesamiento por Lotes**: Maneja grandes volúmenes eficientemente
- ✅ **Procesamiento Paralelo**: Múltiples workers simultáneos
- ✅ **Validación Automática**: Verifica coherencia y calidad de datos
- ✅ **Población Inteligente**: Completa datos faltantes automáticamente
- ✅ **Simetría de Datos**: Mantiene coherencia entre fuentes
- ✅ **Recuperación de Errores**: Checkpoints y reintentos automáticos
- ✅ **Monitoreo Completo**: Logs detallados y métricas en tiempo real
- ✅ **Optimizado para Ubuntu 22.04**: Máximo rendimiento

---

## 🚀 Inicio Rápido

### Instalación Automática

```bash
# 1. Clonar repositorio
git clone <repo-url>
cd PuntaFina_DW_Oro-main

# 2. Ejecutar instalación
chmod +x etl_batch/install.sh
./etl_batch/install.sh

# 3. Configurar credenciales
nano etl_batch/.env

# 4. Ejecutar ETL
source venv/bin/activate
cd etl_batch
python main.py run
```

---

## 📐 Arquitectura

### Componentes Principales

```
etl_batch/
├── config/              # Configuración
│   ├── etl_config.yaml
│   └── .env
├── core/               # Núcleo del sistema
│   ├── batch_processor.py      # Procesamiento por lotes
│   └── data_validator.py       # Validación de datos
├── extractors/         # Extracción
│   ├── database_extractor.py   # De bases de datos
│   └── csv_extractor.py        # De archivos CSV
├── transformers/       # Transformación
│   ├── dimension_builder.py    # Construcción de dimensiones
│   └── fact_builder.py         # Construcción de hechos
├── loaders/           # Carga
│   └── database_loader.py      # A Data Warehouse
├── utils/             # Utilidades
│   ├── logger.py              # Logging
│   └── metrics.py             # Métricas
└── main.py           # Orquestador principal
```

### Flujo de Datos

```
┌─────────────────┐
│  OroCommerce    │───┐
│  OroCRM         │───┼──► Extracción ──► Validación ──► Transformación ──► Carga ──► DW
│  CSV Files      │───┘        │              │               │              │
└─────────────────┘            │              │               │              │
                         (Parallel)    (Auto-Populate)  (Dimensions    (Batch
                          Batch          Symmetry)        + Facts)      Loading)
```

---

## 📊 Datos Procesados

### Fuentes de Datos

| Fuente | Tablas | Registros Estimados |
|--------|--------|---------------------|
| **OroCommerce** | 16 tablas | ~25,000 |
| **OroCRM** | 1 tabla | ~1,200 |
| **CSV Files** | 12 archivos | ~2,100 |
| **TOTAL** | - | ~28,300 |

### Salidas del ETL

| Tipo | Cantidad | Descripción |
|------|----------|-------------|
| **Dimensiones** | 20 tablas | Tablas de contexto |
| **Hechos** | 5 tablas | Tablas de métricas |
| **Registros** | ~145,000 | Total en DW |

---

## ⚙️ Configuración

### Requisitos del Sistema

- **OS**: Ubuntu 22.04 LTS
- **RAM**: 2 GB mínimo, 8 GB recomendado
- **CPU**: 2 cores mínimo, 4+ recomendado
- **Disco**: 5 GB mínimo, 20 GB recomendado
- **Python**: 3.10+
- **PostgreSQL**: 12+

### Configuración de Lotes

```yaml
batch:
  chunk_size: 1000        # Registros por lote
  max_workers: 4          # Procesos paralelos
  timeout: 300            # Timeout (segundos)
  max_retries: 3          # Reintentos
  max_memory_mb: 512      # Memoria por worker
```

### Variables de Entorno

```bash
# Base de datos OroCommerce
ORO_DB_HOST=localhost
ORO_DB_PORT=5432
ORO_DB_NAME=oro_commerce
ORO_DB_USER=oro_user
ORO_DB_PASS=password

# Data Warehouse
DW_ORO_DB_HOST=localhost
DW_ORO_DB_PORT=5432
DW_ORO_DB_NAME=DW_oro
DW_ORO_DB_USER=dw_user
DW_ORO_DB_PASS=password
```

---

## 🔄 Uso

### Comandos Básicos

```bash
# Activar entorno
source venv/bin/activate
cd etl_batch

# Ejecutar ETL completo
python main.py run

# Validar configuración
python main.py validate

# Setup inicial
python main.py setup

# Con configuración personalizada
python main.py run --config custom_config.yaml
```

### Ejecución Automática

#### Cron Job (Diario a las 2 AM)

```bash
crontab -e
# Agregar:
0 2 * * * cd /path/to/etl_batch && /path/to/venv/bin/python main.py run
```

#### Systemd Service

```bash
sudo systemctl enable puntafina-etl
sudo systemctl start puntafina-etl
sudo systemctl status puntafina-etl
```

---

## 📈 Características Avanzadas

### 1. Procesamiento por Lotes

Divide datos grandes en chunks para procesamiento eficiente:

```python
from core.batch_processor import BatchProcessor, BatchConfig

config = BatchConfig(chunk_size=1000, max_workers=4)
processor = BatchProcessor(config)

results = processor.process_dataframe(
    df=my_dataframe,
    process_func=lambda chunk: transform(chunk),
    job_name="my_job"
)
```

### 2. Validación Automática

Valida y puebla datos faltantes:

```python
from core.data_validator import DataValidator

validator = DataValidator(config)
df_validated, report = validator.validate_and_populate(
    df=my_dataframe,
    schema=my_schema,
    source_name="mi_tabla"
)
```

### 3. Mantener Simetría

Fusiona y reconcilia múltiples fuentes:

```python
merged = validator.merge_and_reconcile(
    db_data=oro_data,
    csv_data=csv_data,
    key_columns=['id'],
    priority='db'
)
```

### 4. Checkpoints y Recuperación

Reanuda automáticamente desde último checkpoint:

```
📍 Reanudando desde lote 150
✓ Lote 150/200 (75.0%) - 1000 registros - 2.34s
```

### 5. Streaming para Archivos Grandes

Procesa archivos que no caben en memoria:

```python
from core.batch_processor import StreamingBatchProcessor

streaming = StreamingBatchProcessor(config)
streaming.process_large_file(
    file_path="huge_file.csv",
    process_func=transform,
    job_name="streaming_job"
)
```

---

## 📊 Monitoreo

### Logs

```bash
# Ver en tiempo real
tail -f logs/etl/ETLOrchestrator_*.log

# Buscar errores
grep -r "ERROR" logs/

# Métricas del proceso
cat logs/etl/ETLOrchestrator_*.log | grep "RESUMEN FINAL"
```

### Métricas Automáticas

- ⏱️ Tiempo de ejecución
- 📊 Registros procesados/fallidos
- 💾 Uso de memoria
- 🖥️ Uso de CPU
- ✅ Tasa de éxito

---

## 🐛 Solución de Problemas

### Error Común 1: "Connection refused"

```bash
# Verificar PostgreSQL
sudo systemctl status postgresql
sudo systemctl start postgresql
```

### Error Común 2: "Out of memory"

```yaml
# Reducir en etl_config.yaml
batch:
  chunk_size: 500
  max_workers: 2
```

### Error Común 3: "ModuleNotFoundError"

```bash
source venv/bin/activate
pip install -r etl_batch/requirements.txt
```

Ver [Guía de Troubleshooting](docs/TROUBLESHOOTING.md) completa.

---

## 📚 Documentación

- 📘 [Guía de Instalación](docs/INSTALLATION_GUIDE.md)
- 📗 [Guía de Usuario](docs/USER_GUIDE.md)
- 📕 [Configuración Avanzada](docs/ADVANCED_CONFIGURATION.md)
- 📙 [Solución de Problemas](docs/TROUBLESHOOTING.md)
- 📓 [Referencia API](docs/API_REFERENCE.md)

---

## 🗂️ Estructura del Proyecto

```
PuntaFina_DW_Oro-main/
├── etl_batch/                  # Sistema ETL Batch (NUEVO)
│   ├── config/                 # Configuración
│   ├── core/                   # Núcleo del sistema
│   ├── extractors/             # Extractores
│   ├── transformers/           # Transformadores
│   ├── loaders/                # Cargadores
│   ├── utils/                  # Utilidades
│   ├── docs/                   # Documentación
│   ├── main.py                 # Orquestador principal
│   ├── install.sh              # Script de instalación
│   └── requirements.txt        # Dependencias Python
├── scripts/                    # Scripts originales (referencia)
├── data/                       # Datos
│   ├── inputs/                 # CSVs de entrada
│   ├── outputs/                # Parquet/CSV de salida
│   ├── staging/                # Área temporal
│   └── checkpoints/            # Checkpoints de recuperación
├── logs/                       # Logs del sistema
│   ├── etl/                    # Logs ETL
│   ├── audit/                  # Auditoría
│   └── errors/                 # Solo errores
├── venv/                       # Entorno virtual Python
└── README.md                   # Este archivo
```

---

## 🔄 Migración desde Sistema Anterior

Si vienes del sistema ETL anterior:

1. **Backup de datos actuales**:
   ```bash
   pg_dump DW_oro > backup_old_system.sql
   ```

2. **Instalar nuevo sistema**:
   ```bash
   ./etl_batch/install.sh
   ```

3. **Configurar credenciales**:
   ```bash
   cp config/.env etl_batch/.env
   nano etl_batch/.env
   ```

4. **Ejecutar migración**:
   ```bash
   cd etl_batch
   python main.py run
   ```

5. **Validar resultados**:
   ```sql
   SELECT COUNT(*) FROM dim_fecha;
   SELECT COUNT(*) FROM fact_ventas;
   ```

---

## 🤝 Contribución

Para contribuir:

1. Fork del repositorio
2. Crear branch de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push al branch (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo [LICENSE](LICENSE) para más detalles.

---

## 📞 Contacto y Soporte

- 📧 Email: soporte@puntafina.com
- 📚 Documentación: `etl_batch/docs/`
- 🐛 Issues: GitHub Issues

---

## 🎯 Roadmap

### Versión Actual: 1.0

- ✅ Procesamiento por lotes
- ✅ Validación automática
- ✅ Población inteligente
- ✅ Checkpoints y recuperación
- ✅ Monitoreo completo

### Próximas Versiones

- [ ] Dashboard de monitoreo web
- [ ] API REST para consultas
- [ ] Integración con Apache Airflow
- [ ] Soporte para más fuentes de datos
- [ ] Machine Learning para detección de anomalías

---

## ✅ Estado del Proyecto

- **Estado**: ✅ Production Ready
- **Versión**: 1.0.0
- **Última actualización**: 2026-01-01
- **Mantenimiento**: Activo
- **Estabilidad**: Alta

---

**Desarrollado con ❤️ para PuntaFina** 🏪
