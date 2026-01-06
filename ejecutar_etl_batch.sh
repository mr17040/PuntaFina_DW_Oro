#!/bin/bash
# ============================================================================
# EJECUTAR ETL BATCH ACTUALIZADO
# ============================================================================
# Ejecuta el ETL completo con la nueva estructura y limpieza automática

set -e  # Salir si hay error

echo "================================================================================"
echo "                  PUNTAFINA ETL BATCH - EJECUCIÓN COMPLETA"
echo "================================================================================"
echo ""

# Directorio base
cd "$(dirname "$0")"
ETL_DIR="/root/PuntaFina_DW_Oro/etl_batch"
BASE_DIR="/root/PuntaFina_DW_Oro"

# Cargar variables de entorno
if [ -f "$BASE_DIR/.env" ]; then
    echo "✓ Cargando variables de entorno..."
    set -a
    source "$BASE_DIR/.env"
    set +a
else
    echo "❌ Archivo .env no encontrado en $BASE_DIR"
    exit 1
fi

# Verificar conexiones
echo ""
echo "🔍 Verificando conexiones a bases de datos..."

# Test OroCommerce
PGPASSWORD="$ORO_DB_PASS" psql -h "$ORO_DB_HOST" -U "$ORO_DB_USER" -d "$ORO_DB_NAME" -c "SELECT COUNT(*) FROM oro_order" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✓ Conexión a OroCommerce OK"
else
    echo "   ❌ Error conectando a OroCommerce"
    exit 1
fi

# Test Data Warehouse
PGPASSWORD="$DW_DB_PASS" psql -h "$DW_DB_HOST" -U "$DW_DB_USER" -d "$DW_DB_NAME" -c "SELECT 1" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✓ Conexión a Data Warehouse OK"
else
    echo "   ❌ Error conectando a Data Warehouse"
    exit 1
fi

echo ""
echo "🚀 Iniciando ETL batch..."
echo ""

# Ejecutar ETL
cd "$ETL_DIR"
python3 main.py run

echo ""
echo "================================================================================"
echo "✅ ETL COMPLETADO"
echo "================================================================================"
echo ""

# Mostrar resumen final simple
echo "📊 RESUMEN DE TABLAS:"
PGPASSWORD="$DW_DB_PASS" psql -h "$DW_DB_HOST" -U "$DW_DB_USER" -d "$DW_DB_NAME" -t -c "
SELECT 
    'fact_ventas: ' || COUNT(*) || ' registros'
FROM fact_ventas;
" 2>/dev/null || echo "⚠️  No se pudo obtener resumen"

echo ""
echo "✅ Para ver detalles ejecuta: psql -h localhost -U sa -d datawarehouse_bi"
echo ""
