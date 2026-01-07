#!/usr/bin/env python3
"""
Script consolidado para cargar todo el Data Warehouse desde las fuentes de origen:
- orocommerce: clientes, órdenes, productos, line items
- CSVs: inventario, finanzas, contabilidad
"""

import sys
import subprocess

print("="*80)
print("CARGA COMPLETA DEL DATA WAREHOUSE - PUNTAFINA")
print("="*80)

# 1. Cargar dimensiones
print("\n🔹 PASO 1: Cargando dimensiones desde origen...")
result = subprocess.run(['python3', 'cargar_dimensiones_origen.py'], capture_output=True, text=True)
if result.returncode != 0:
    print(f"❌ Error cargando dimensiones:\n{result.stderr}")
    sys.exit(1)
print(result.stdout)

# 2. Cargar facts
print("\n🔹 PASO 2: Cargando facts desde origen...")
result = subprocess.run(['python3', 'cargar_todos_facts.py'], capture_output=True, text=True)
if result.returncode != 0:
    print(f"❌ Error cargando facts:\n{result.stderr}")
    sys.exit(1)
print(result.stdout)

# 3. Resumen final
print("\n🔹 PASO 3: Generando resumen...")
import psycopg2

conn = psycopg2.connect(
    host='104.156.246.237', port=5432,
    dbname='datawarehouse_bi', user='sa', password='IngDatos123*'
)
cursor = conn.cursor()

print("\n" + "="*80)
print("RESUMEN DEL DATA WAREHOUSE")
print("="*80)

# Dimensiones
cursor.execute("""
    SELECT COUNT(*) FROM dim_fecha UNION ALL
    SELECT COUNT(*) FROM dim_cliente UNION ALL
    SELECT COUNT(*) FROM dim_producto UNION ALL
    SELECT COUNT(*) FROM dim_orden UNION ALL
    SELECT COUNT(*) FROM dim_almacen UNION ALL
    SELECT COUNT(*) FROM dim_proveedor UNION ALL
    SELECT COUNT(*) FROM dim_tipo_movimiento UNION ALL
    SELECT COUNT(*) FROM dim_centro_costo UNION ALL
    SELECT COUNT(*) FROM dim_tipo_transaccion UNION ALL
    SELECT COUNT(*) FROM dim_cuenta_contable UNION ALL
    SELECT COUNT(*) FROM dim_impuestos UNION ALL
    SELECT COUNT(*) FROM dim_usuario UNION ALL
    SELECT COUNT(*) FROM dim_periodo
""")
dims = ['fecha', 'cliente', 'producto', 'orden', 'almacen', 'proveedor', 
        'tipo_movimiento', 'centro_costo', 'tipo_transaccion', 'cuenta_contable',
        'impuestos', 'usuario', 'periodo']
results = cursor.fetchall()

print("\n📊 DIMENSIONES:")
total_dims = 0
for i, (dim, count) in enumerate(zip(dims, results)):
    total_dims += count[0]
    print(f"  ✅ dim_{dim:25} {count[0]:>10,} registros")

# Facts
cursor.execute("""
    SELECT COUNT(*) FROM fact_ventas UNION ALL
    SELECT COUNT(*) FROM fact_inventario UNION ALL
    SELECT COUNT(*) FROM fact_transacciones UNION ALL
    SELECT COUNT(*) FROM fact_balance UNION ALL
    SELECT COUNT(*) FROM fact_estado_resultados
""")
facts = ['ventas', 'inventario', 'transacciones', 'balance', 'estado_resultados']
results = cursor.fetchall()

print("\n📈 FACTS:")
total_facts = 0
for fact, count in zip(facts, results):
    total_facts += count[0]
    status = '✅' if count[0] > 0 else '⚠️'
    print(f"  {status} fact_{fact:25} {count[0]:>10,} registros")

print("\n" + "="*80)
print(f"TOTAL REGISTROS: {total_dims + total_facts:,}")
print(f"  - Dimensiones:  {total_dims:,}")
print(f"  - Facts:        {total_facts:,}")
print("="*80)

cursor.close()
conn.close()

print("\n✅ CARGA COMPLETA FINALIZADA EXITOSAMENTE")
print("="*80)
