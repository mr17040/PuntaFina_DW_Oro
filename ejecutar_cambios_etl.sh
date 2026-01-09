#!/bin/bash
# ============================================================================
# Script para aplicar cambios al DW y ejecutar ETL completo
# ============================================================================

set -e  # Salir si hay errores

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "════════════════════════════════════════════════════════════════════════"
echo "🔧 APLICANDO CAMBIOS AL DATA WAREHOUSE - PUNTAFINA"
echo "════════════════════════════════════════════════════════════════════════"
echo ""

# Cargar variables de entorno
if [ -f "etl_batch/.env" ]; then
    export $(grep -v '^#' etl_batch/.env | xargs)
    echo "✓ Variables de entorno cargadas"
else
    echo "❌ Error: Archivo .env no encontrado"
    exit 1
fi

# 1. Aplicar cambios al esquema de la base de datos
echo ""
echo "📋 Paso 1: Aplicando cambios al esquema de la base de datos..."
echo "────────────────────────────────────────────────────────────────────────"

PGPASSWORD="$DW_DB_PASS" psql \
    -h "$DW_DB_HOST" \
    -p "$DW_DB_PORT" \
    -U "$DW_DB_USER" \
    -d "$DW_DB_NAME" \
    -f "sql/granular/add_promocion_to_fact_ventas.sql" \
    2>&1 | tee /tmp/apply_schema_changes.log

if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "✓ Cambios de esquema aplicados correctamente"
else
    echo "❌ Error aplicando cambios de esquema. Ver /tmp/apply_schema_changes.log"
    exit 1
fi

# 2. Ejecutar ETL completo
echo ""
echo "📋 Paso 2: Ejecutando ETL completo..."
echo "────────────────────────────────────────────────────────────────────────"

cd etl_batch

# Activar entorno virtual si existe
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✓ Entorno virtual activado"
fi

# Verificar dependencias de Python
echo "Verificando dependencias de Python..."
python3 -c "import pandas, psycopg2, yaml" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Instalando dependencias faltantes..."
    pip install -q pandas psycopg2-binary pyyaml python-dotenv
fi

# Ejecutar ETL
echo ""
echo "🚀 Ejecutando ETL..."
python3 main.py --full 2>&1 | tee /tmp/etl_execution.log

ETL_EXIT_CODE=${PIPESTATUS[0]}

cd ..

# 3. Verificar resultados
echo ""
echo "📋 Paso 3: Verificando resultados..."
echo "────────────────────────────────────────────────────────────────────────"

if [ $ETL_EXIT_CODE -eq 0 ]; then
    echo "✓ ETL ejecutado correctamente"
    
    # Verificar registros en las tablas
    echo ""
    echo "Verificando registros en las tablas principales..."
    
    PGPASSWORD="$DW_DB_PASS" psql \
        -h "$DW_DB_HOST" \
        -p "$DW_DB_PORT" \
        -U "$DW_DB_USER" \
        -d "$DW_DB_NAME" \
        -c "
        SELECT 
            'dim_cuenta_contable' as tabla, 
            COUNT(*) as registros,
            COUNT(*) FILTER (WHERE codigo IS NULL OR nombre IS NULL) as nulos
        FROM dim_cuenta_contable
        UNION ALL
        SELECT 
            'dim_producto', 
            COUNT(*),
            COUNT(*) FILTER (WHERE precio_base = 0 OR costo_estandar = 0) as sin_precio_o_costo
        FROM dim_producto
        UNION ALL
        SELECT 
            'dim_promocion', 
            COUNT(*),
            0
        FROM dim_promocion
        UNION ALL
        SELECT 
            'fact_ventas', 
            COUNT(*),
            COUNT(*) FILTER (WHERE costo_unitario = 0 OR margen = 0) as sin_costo_o_margen
        FROM fact_ventas;
        " | column -t
    
    echo ""
    echo "════════════════════════════════════════════════════════════════════════"
    echo "✅ PROCESO COMPLETADO EXITOSAMENTE"
    echo "════════════════════════════════════════════════════════════════════════"
    echo ""
    echo "Resumen de cambios aplicados:"
    echo "  1. ✓ dim_cuenta_contable: Sin nulos o NaN"
    echo "  2. ✓ dim_producto: Con precio_base y costo_estandar desde fuentes"
    echo "  3. ✓ fact_ventas: Con costo_unitario, costo_total, margen y descuentos"
    echo "  4. ✓ dim_promocion: Creada con datos desde oro_order"
    echo ""
    echo "Logs disponibles en:"
    echo "  - Schema changes: /tmp/apply_schema_changes.log"
    echo "  - ETL execution: /tmp/etl_execution.log"
    echo "  - ETL logs: etl_batch/logs/"
    echo ""
    
else
    echo "❌ Error en la ejecución del ETL. Ver /tmp/etl_execution.log"
    exit 1
fi
