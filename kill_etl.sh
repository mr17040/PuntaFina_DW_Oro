#!/bin/bash
# Matar procesos ETL colgados

echo "🛑 Matando procesos ETL..."

# Matar python3 main.py
pkill -9 -f "python3.*main.py"

# Matar scripts bash
pkill -9 -f "ejecutar_etl_batch.sh"

# Matar psql colgados
pkill -9 -f "psql.*datawarehouse_bi"

echo "✅ Procesos terminados"

# Verificar estado
echo ""
echo "📊 Estado actual de la base de datos:"
PGPASSWORD="IngDatos123*" psql -h localhost -U sa -d datawarehouse_bi -c "
SELECT 
    'fact_ventas' as tabla, COUNT(*) as registros 
FROM fact_ventas
UNION ALL
SELECT 'dim_cliente', COUNT(*) FROM dim_cliente
UNION ALL  
SELECT 'dim_producto', COUNT(*) FROM dim_producto
ORDER BY 1;
"

echo ""
echo "🔍 Procesos activos:"
ps aux | grep -E "python3|psql|postgres" | grep -v grep | head -5
