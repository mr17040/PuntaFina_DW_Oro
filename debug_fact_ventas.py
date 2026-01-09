#!/usr/bin/env python3
"""
Debug: Probar fact_ventas directamente
"""
import os
import sys

os.chdir("/Users/elsalvador/project/PuntaFina_DW_Oro")
sys.path.insert(0, "/Users/elsalvador/project/PuntaFina_DW_Oro/etl_batch")

from dotenv import load_dotenv

load_dotenv("/Users/elsalvador/project/PuntaFina_DW_Oro/etl_batch/.env")

import psycopg2
from psycopg2.extras import execute_values
import pandas as pd

from transformers.complete_fact_builder import CompleteFactBuilder

DW_CONFIG = {
    "host": os.getenv("DW_DB_HOST"),
    "port": int(os.getenv("DW_DB_PORT", 5432)),
    "dbname": os.getenv("DW_DB_NAME"),
    "user": os.getenv("DW_DB_USER"),
    "password": os.getenv("DW_DB_PASS"),
}

print("=" * 60)
print("TEST: fact_ventas")
print("=" * 60)

# Primero asegurar que las dimensiones existen
conn = psycopg2.connect(**DW_CONFIG)
conn.autocommit = True
cursor = conn.cursor()

print("\nVerificando dimensiones necesarias:")
dims = [
    "dim_fecha",
    "dim_producto",
    "dim_cliente",
    "dim_orden",
    "dim_usuario",
    "dim_almacen",
    "dim_impuestos",
    "dim_promocion",
]
for dim in dims:
    cursor.execute(f"SELECT COUNT(*) FROM {dim}")
    count = cursor.fetchone()[0]
    print(f"  {dim}: {count} registros")

# Construir fact_ventas
print("\nConstruyendo fact_ventas...")
builder = CompleteFactBuilder(dw_conn=conn)
df = builder.build_fact_ventas()

print(f"\nDataFrame resultante: {len(df)} registros")
print(f"Columnas: {df.columns.tolist()}")
print(f"\nPrimeras 3 filas:")
print(df.head(3))

print(f"\nEstadísticas de costos:")
print(f"  costo_unitario > 0: {(df['costo_unitario'] > 0).sum()} registros")
print(f"  costo_total > 0: {(df['costo_total'] > 0).sum()} registros")
print(f"  margen promedio: {df['margen'].mean():.2f}")

# Intentar insertar
print("\n" + "=" * 40)
print("Insertando en fact_ventas...")

cursor.execute("TRUNCATE TABLE fact_ventas CASCADE")
print("TRUNCATE ejecutado")

cursor.execute("SELECT COUNT(*) FROM fact_ventas")
count_after_truncate = cursor.fetchone()[0]
print(f"fact_ventas después de TRUNCATE: {count_after_truncate}")

# Quitar venta_id ya que es serial (autogenerado)
if "venta_id" in df.columns:
    df = df.drop(columns=["venta_id"])
    print("Quitado 'venta_id' (será autogenerado)")

columns = df.columns.tolist()
values = [tuple(row) for row in df.values]

insert_query = f"""
    INSERT INTO fact_ventas ({', '.join(columns)})
    VALUES %s
"""

print(f"Query: INSERT INTO fact_ventas ({', '.join(columns[:5])}...)")
print(f"Ejemplo de valores: {values[0] if values else 'vacío'}")

try:
    execute_values(cursor, insert_query, values, page_size=1000)
    print("execute_values completado sin error")
except Exception as e:
    print(f"ERROR en execute_values: {e}")
    import traceback

    traceback.print_exc()

# Verificar
cursor.execute("SELECT COUNT(*) FROM fact_ventas")
count_final = cursor.fetchone()[0]
print(f"fact_ventas FINAL: {count_final} registros")

# Verificar datos de costos
cursor.execute(
    """
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN costo_unitario > 0 THEN 1 ELSE 0 END) as con_costo,
        AVG(costo_unitario) as avg_costo,
        AVG(margen) as avg_margen
    FROM fact_ventas
"""
)
row = cursor.fetchone()
print(f"\nEstadísticas en DB:")
print(f"  Total: {row[0]}")
print(f"  Con costo: {row[1]}")
print(f"  Costo promedio: {row[2]}")
print(f"  Margen promedio: {row[3]}")

cursor.close()
conn.close()

# Verificación final con nueva conexión
print("\n" + "=" * 40)
print("Verificación con nueva conexión:")
conn = psycopg2.connect(**DW_CONFIG)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM fact_ventas")
count_verify = cursor.fetchone()[0]
print(f"fact_ventas verificación: {count_verify} registros")

# Mostrar ejemplo de registro
cursor.execute("SELECT * FROM fact_ventas LIMIT 1")
row = cursor.fetchone()
cursor.execute(
    "SELECT column_name FROM information_schema.columns WHERE table_name = 'fact_ventas' ORDER BY ordinal_position"
)
cols = [r[0] for r in cursor.fetchall()]
if row:
    print("\nEjemplo de registro:")
    for col, val in zip(cols, row):
        print(f"  {col}: {val}")

cursor.close()
conn.close()

print("\n✅ Test completado")
