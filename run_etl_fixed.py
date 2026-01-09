#!/usr/bin/env python3
"""
Ejecutar ETL completo y verificar resultados
"""
import os
import sys
import time

os.chdir("/Users/elsalvador/project/PuntaFina_DW_Oro")
sys.path.insert(0, "/Users/elsalvador/project/PuntaFina_DW_Oro/etl_batch")

from dotenv import load_dotenv

load_dotenv("/Users/elsalvador/project/PuntaFina_DW_Oro/etl_batch/.env")

import psycopg2
from psycopg2.extras import execute_values
import pandas as pd

from transformers.complete_dimension_builder import CompleteDimensionBuilder
from transformers.complete_fact_builder import CompleteFactBuilder

DW_CONFIG = {
    "host": os.getenv("DW_DB_HOST"),
    "port": int(os.getenv("DW_DB_PORT", 5432)),
    "dbname": os.getenv("DW_DB_NAME"),
    "user": os.getenv("DW_DB_USER"),
    "password": os.getenv("DW_DB_PASS"),
}

print("=" * 60)
print("ETL COMPLETO - PuntaFina DW")
print("=" * 60)
start_time = time.time()

# Conexión con autocommit
conn = psycopg2.connect(**DW_CONFIG)
conn.autocommit = True
cursor = conn.cursor()

# 1. LIMPIAR FACT TABLES PRIMERO
print("\n1. Limpiando fact tables...")
cursor.execute(
    "TRUNCATE TABLE fact_ventas, fact_inventario, fact_transacciones CASCADE"
)
print("   ✓ Fact tables truncadas")

# 2. CONSTRUIR Y CARGAR DIMENSIONES
print("\n2. Construyendo dimensiones...")
builder = CompleteDimensionBuilder()

dimensions = [
    ("dim_fecha", builder.build_dim_fecha, False),
    ("dim_producto", builder.build_dim_producto, False),
    ("dim_cliente", builder.build_dim_cliente, False),
    ("dim_orden", builder.build_dim_orden, False),
    ("dim_usuario", builder.build_dim_usuario, False),
    ("dim_cuenta_contable", builder.build_dim_cuenta_contable, False),
    (
        "dim_impuestos",
        builder.build_dim_impuestos,
        True,
    ),  # Necesita OVERRIDING SYSTEM VALUE
    ("dim_promocion", builder.build_dim_promocion, False),
    ("dim_almacen", builder.build_dim_almacen, False),
    ("dim_proveedor", builder.build_dim_proveedor, False),
    ("dim_tipo_movimiento", builder.build_dim_tipo_movimiento, False),
    ("dim_centro_costo", builder.build_dim_centro_costo, False),
    ("dim_tipo_transaccion", builder.build_dim_tipo_transaccion, False),
]

total_dims = 0
for dim_name, method, override_id in dimensions:
    try:
        df = method()
        if df is not None and len(df) > 0:
            cursor.execute(f"TRUNCATE TABLE {dim_name} CASCADE")

            columns = df.columns.tolist()
            values = [tuple(row) for row in df.values]

            if override_id:
                insert_query = f"INSERT INTO {dim_name} ({', '.join(columns)}) OVERRIDING SYSTEM VALUE VALUES %s"
            else:
                insert_query = (
                    f"INSERT INTO {dim_name} ({', '.join(columns)}) VALUES %s"
                )

            execute_values(cursor, insert_query, values, page_size=1000)
            total_dims += len(df)
            print(f"   ✓ {dim_name}: {len(df):,} registros")
        else:
            print(f"   ⚠️ {dim_name}: sin datos")
    except Exception as e:
        print(f"   ❌ {dim_name}: {e}")

# Insertar cliente por defecto si no existe
try:
    cursor.execute(
        """
        INSERT INTO dim_cliente (cliente_id, cliente_externo_id, codigo_cliente, nombre, tipo_cliente, segmento, activo, fecha_registro, created_at)
        VALUES (1, 0, 'CLI-DEFAULT', 'Cliente por Defecto', 'B2B', 'General', true, '2020-01-01', NOW())
        ON CONFLICT (cliente_id) DO NOTHING
    """
    )
except:
    pass

print(f"\n   Total dimensiones: {total_dims:,} registros")

# 3. CONSTRUIR Y CARGAR FACT_VENTAS
print("\n3. Construyendo fact_ventas...")
fact_builder = CompleteFactBuilder(dw_conn=conn)
df_fact = fact_builder.build_fact_ventas()

if df_fact is not None and len(df_fact) > 0:
    cursor.execute("TRUNCATE TABLE fact_ventas CASCADE")

    columns = df_fact.columns.tolist()
    values = [tuple(row) for row in df_fact.values]

    insert_query = f"INSERT INTO fact_ventas ({', '.join(columns)}) VALUES %s"
    execute_values(cursor, insert_query, values, page_size=1000)
    print(f"   ✓ fact_ventas: {len(df_fact):,} registros")
else:
    print("   ⚠️ fact_ventas: sin datos")

cursor.close()
conn.close()

elapsed = time.time() - start_time

# 4. VERIFICACIÓN FINAL
print("\n4. Verificación final...")
conn = psycopg2.connect(**DW_CONFIG)
cursor = conn.cursor()

tables = [
    "dim_fecha",
    "dim_producto",
    "dim_cliente",
    "dim_orden",
    "dim_usuario",
    "dim_cuenta_contable",
    "dim_impuestos",
    "dim_promocion",
    "dim_almacen",
    "dim_proveedor",
    "dim_tipo_movimiento",
    "dim_centro_costo",
    "dim_tipo_transaccion",
    "fact_ventas",
]

total = 0
print("\n   Conteo de registros:")
for table in tables:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        total += count
        status = "✅" if count > 0 else "⚠️"
        print(f"   {status} {table}: {count:,}")
    except Exception as e:
        print(f"   ❌ {table}: {e}")

# Verificar calidad de datos
print("\n   Verificación de calidad:")

# dim_producto - precios/costos
cursor.execute(
    """
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN precio_base > 0 THEN 1 ELSE 0 END) as con_precio,
        SUM(CASE WHEN costo_estandar > 0 THEN 1 ELSE 0 END) as con_costo
    FROM dim_producto
"""
)
row = cursor.fetchone()
pct_precio = 100 * row[1] / row[0] if row[0] > 0 else 0
pct_costo = 100 * row[2] / row[0] if row[0] > 0 else 0
print(f"   dim_producto: {pct_precio:.1f}% con precio, {pct_costo:.1f}% con costo")

# fact_ventas - costos/margen
cursor.execute(
    """
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN costo_unitario > 0 THEN 1 ELSE 0 END) as con_costo,
        AVG(margen) as avg_margen
    FROM fact_ventas
"""
)
row = cursor.fetchone()
pct_costo_fv = 100 * row[1] / row[0] if row[0] > 0 else 0
avg_margen = row[2] if row[2] else 0
print(
    f"   fact_ventas: {pct_costo_fv:.1f}% con costo, margen promedio: ${avg_margen:.2f}"
)

# dim_cuenta_contable - sin NaN
cursor.execute(
    """
    SELECT COUNT(*) FROM dim_cuenta_contable 
    WHERE codigo LIKE '%nan%' OR nombre LIKE '%nan%'
"""
)
nan_count = cursor.fetchone()[0]
print(f"   dim_cuenta_contable: {nan_count} registros con NaN")

cursor.close()
conn.close()

print(f"\n{'='*60}")
print(f"✅ ETL COMPLETADO en {elapsed:.1f} segundos")
print(f"   Total registros: {total:,}")
print(f"{'='*60}")
