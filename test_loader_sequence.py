#!/usr/bin/env python3
"""Test del reset de secuencias en el loader"""
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('/root/PuntaFina_DW_Oro/etl_batch/.env')

# Conexión a DW
dw_conn = psycopg2.connect(
    host=os.getenv('DW_DB_HOST'),
    port=int(os.getenv('DW_DB_PORT', 5432)),
    database=os.getenv('DW_DB_NAME'),
    user=os.getenv('DW_DB_USER'),
    password=os.getenv('DW_DB_PASS')
)

# Leer parquet
df = pd.read_parquet('/root/PuntaFina_DW_Oro/data/outputs/parquet/dim_cuenta_contable.parquet')
print(f"Parquet tiene {len(df)} registros")
print(f"Columnas: {df.columns.tolist()}")
print(f"Primeras columnas que terminan en _id: {[c for c in df.columns if c.endswith('_id')]}")

# Ver columnas de la tabla en BD
cursor = dw_conn.cursor()
cursor.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'dim_cuenta_contable' 
    AND table_schema = 'public'
    ORDER BY ordinal_position
""")
bd_columns = [row[0] for row in cursor.fetchall()]
print(f"\nColumnas en BD: {bd_columns}")

# Ver cuál es la primary key
cursor.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'dim_cuenta_contable' 
    AND table_schema = 'public'
    AND column_name LIKE '%_id'
    AND ordinal_position = 1
""")
result = cursor.fetchone()
print(f"\nPrimera columna _id en BD: {result}")

# Ver secuencia
cursor.execute("SELECT sequencename FROM pg_sequences WHERE sequencename LIKE '%cuenta%'")
print(f"Secuencias: {cursor.fetchall()}")

# Mapeo de columnas
df_id_col = next((col for col in df.columns if col.endswith('_id')), None)
print(f"\nColumna ID en parquet: {df_id_col}")
if df_id_col:
    max_id = df[df_id_col].max()
    print(f"Max ID en parquet: {max_id}")
    
    if result:
        db_id_col = result[0]
        seq_name = f"dim_cuenta_contable_{db_id_col}_seq"
        print(f"Nombre de secuencia a resetear: {seq_name}")
        
        # Resetear secuencia
        try:
            cursor.execute(f"SELECT setval('{seq_name}', {int(max_id)}, true)")
            dw_conn.commit()
            print(f"✓ Secuencia reseteada a {int(max_id)}")
            
            # Verificar
            cursor.execute(f"SELECT last_value FROM {seq_name}")
            print(f"Valor actual de secuencia: {cursor.fetchone()[0]}")
        except Exception as e:
            print(f"✗ Error: {e}")

cursor.close()
dw_conn.close()
