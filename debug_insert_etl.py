#!/usr/bin/env python3
"""
Debug: Probar inserts individuales con execute_values
"""
import os
import sys

# Cambiar al directorio del proyecto
os.chdir("/Users/elsalvador/project/PuntaFina_DW_Oro")
sys.path.insert(0, "/Users/elsalvador/project/PuntaFina_DW_Oro/etl_batch")

from dotenv import load_dotenv

load_dotenv("/Users/elsalvador/project/PuntaFina_DW_Oro/etl_batch/.env")

import psycopg2
from psycopg2.extras import execute_values
import pandas as pd

# Configuración
DW_CONFIG = {
    "host": os.getenv("DW_DB_HOST"),
    "port": int(os.getenv("DW_DB_PORT", 5432)),
    "dbname": os.getenv("DW_DB_NAME"),
    "user": os.getenv("DW_DB_USER"),
    "password": os.getenv("DW_DB_PASS"),
}

print(f"Conectando a: {DW_CONFIG['host']}:{DW_CONFIG['port']}/{DW_CONFIG['dbname']}")

# 1. Probar insert directo con execute_values - datos mínimos
print("\n" + "=" * 60)
print("TEST 1: CompleteDimensionBuilder para dim_fecha")
print("=" * 60)

from transformers.complete_dimension_builder import CompleteDimensionBuilder

builder = CompleteDimensionBuilder()
df = builder.build_dim_fecha()

print(f"DataFrame creado: {len(df)} registros")
print(f"Columnas: {df.columns.tolist()}")
print(f"Primeras filas:")
print(df.head(3))

# Insertar con el mismo método que usa main.py
conn = psycopg2.connect(**DW_CONFIG)
conn.autocommit = True
cursor = conn.cursor()

# Verificar conteo ANTES
cursor.execute("SELECT COUNT(*) FROM dim_fecha")
count_before = cursor.fetchone()[0]
print(f"\ndim_fecha ANTES: {count_before} registros")

# Truncar
cursor.execute("TRUNCATE TABLE dim_fecha CASCADE")
print("TRUNCATE ejecutado")

# Verificar después de truncar
cursor.execute("SELECT COUNT(*) FROM dim_fecha")
count_after_truncate = cursor.fetchone()[0]
print(f"dim_fecha DESPUÉS de TRUNCATE: {count_after_truncate} registros")

# Preparar datos
columns = df.columns.tolist()
values = [tuple(row) for row in df.values]

print(f"Columnas: {columns}")
print(f"Ejemplo de valor: {values[0] if values else 'vacío'}")

insert_query = f"""
    INSERT INTO dim_fecha ({', '.join(columns)})
    VALUES %s
"""

try:
    execute_values(cursor, insert_query, values, page_size=1000)
    print("execute_values completado sin error")
except Exception as e:
    print(f"ERROR en execute_values: {e}")
    import traceback

    traceback.print_exc()

# Verificar DESPUÉS
cursor.execute("SELECT COUNT(*) FROM dim_fecha")
count_after_insert = cursor.fetchone()[0]
print(f"dim_fecha DESPUÉS de INSERT: {count_after_insert} registros")

# Mostrar lo que hay
cursor.execute(
    "SELECT fecha_id, fecha, mes_nombre FROM dim_fecha ORDER BY fecha_id LIMIT 5"
)
rows = cursor.fetchall()
print(f"Primeros 5 registros:")
for row in rows:
    print(f"  {row}")

cursor.close()
conn.close()

# 2. Verificación final con nueva conexión
print("\n" + "=" * 60)
print("TEST 2: Verificación con nueva conexión")
print("=" * 60)

conn = psycopg2.connect(**DW_CONFIG)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM dim_fecha")
count_verify = cursor.fetchone()[0]
print(f"dim_fecha verificación final: {count_verify} registros")
cursor.close()
conn.close()

print("\n✅ Debug completado")
