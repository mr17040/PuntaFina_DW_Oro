#!/bin/bash
# Script de verificación de la actualización del README

echo "=========================================="
echo "VERIFICACIÓN DE ACTUALIZACIÓN DEL README"
echo "=========================================="
echo ""

echo "📊 Verificando conteos en la base de datos..."
echo ""

# fact_ventas
VENTAS=$(sudo -u postgres psql -d datawarehouse_bi -tAc "SELECT COUNT(*) FROM fact_ventas;")
echo "✅ fact_ventas: $VENTAS registros"

# fact_inventario
INVENTARIO=$(sudo -u postgres psql -d datawarehouse_bi -tAc "SELECT COUNT(*) FROM fact_inventario;")
echo "✅ fact_inventario: $INVENTARIO registros"

# fact_transacciones
TRANSACCIONES=$(sudo -u postgres psql -d datawarehouse_bi -tAc "SELECT COUNT(*) FROM fact_transacciones;")
echo "✅ fact_transacciones: $TRANSACCIONES registros"

# fact_estado_resultados
ESTADO=$(sudo -u postgres psql -d datawarehouse_bi -tAc "SELECT COUNT(*) FROM fact_estado_resultados;")
echo "✅ fact_estado_resultados: $ESTADO registros"

# fact_balance
BALANCE=$(sudo -u postgres psql -d datawarehouse_bi -tAc "SELECT COUNT(*) FROM fact_balance;")
echo "✅ fact_balance: $BALANCE registros"

echo ""
echo "📋 Verificando dimensiones..."
echo ""

# dim_cliente
CLIENTES=$(sudo -u postgres psql -d datawarehouse_bi -tAc "SELECT COUNT(*) FROM dim_cliente;")
echo "✅ dim_cliente: $CLIENTES clientes"

# dim_producto
PRODUCTOS=$(sudo -u postgres psql -d datawarehouse_bi -tAc "SELECT COUNT(*) FROM dim_producto;")
echo "✅ dim_producto: $PRODUCTOS productos"

# dim_fecha
FECHAS=$(sudo -u postgres psql -d datawarehouse_bi -tAc "SELECT COUNT(*) FROM dim_fecha;")
echo "✅ dim_fecha: $FECHAS fechas"

# Total tablas
TOTAL_TABLAS=$(sudo -u postgres psql -d datawarehouse_bi -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';")
echo "✅ Total tablas: $TOTAL_TABLAS tablas"

echo ""
echo "📝 Verificando archivos generados..."
echo ""

if [ -f "README.md" ]; then
    echo "✅ README.md existe"
    LINES=$(wc -l < README.md)
    echo "   - $LINES líneas"
fi

if [ -f "docs/database_tables_complete.md" ]; then
    echo "✅ docs/database_tables_complete.md existe"
fi

if [ -f "docs/RESUMEN_ACTUALIZACION_README.md" ]; then
    echo "✅ docs/RESUMEN_ACTUALIZACION_README.md existe"
fi

if [ -f "ACTUALIZACION_COMPLETADA.md" ]; then
    echo "✅ ACTUALIZACION_COMPLETADA.md existe"
fi

echo ""
echo "🎯 RESUMEN"
echo "=========================================="
echo "Total de hechos: $((VENTAS + INVENTARIO + TRANSACCIONES + ESTADO + BALANCE)) registros"
echo "Dimensiones principales: $CLIENTES clientes, $PRODUCTOS productos, $FECHAS fechas"
echo "Total tablas en BD: $TOTAL_TABLAS"
echo "=========================================="
echo ""
echo "✅ VERIFICACIÓN COMPLETADA"
echo ""
