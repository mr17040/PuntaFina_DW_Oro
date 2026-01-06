#!/bin/bash
echo "=== Estado del Sistema ETL ==="
echo ""

echo "📊 Registros en tablas fact:"
PGPASSWORD="IngDatos123*" psql -h localhost -U sa -d datawarehouse_bi -t -A -c "
SELECT 'fact_ventas', COUNT(*) FROM fact_ventas
UNION ALL SELECT 'fact_inventario', COUNT(*) FROM fact_inventario  
UNION ALL SELECT 'fact_transacciones', COUNT(*) FROM fact_transacciones
UNION ALL SELECT 'fact_balance', COUNT(*) FROM fact_balance
UNION ALL SELECT 'fact_estado_resultados', COUNT(*) FROM fact_estado_resultados
" | column -t -s'|'

echo ""
echo "📁 CSVs creados:"
ls -lh /root/PuntaFina_DW_Oro/data/inputs/fact_*.csv 2>/dev/null | awk '{print $9, $5}'

echo ""
echo "🔄 Procesos ETL activos:"
ps aux | grep -E "[p]ython3.*main.py|[e]jecutar_etl" | awk '{print $2, $11, $12, $13}'

echo ""
echo "✅ Listo"
