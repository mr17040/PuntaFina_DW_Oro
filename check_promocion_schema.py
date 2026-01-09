#!/usr/bin/env python3
import psycopg2

conn = psycopg2.connect(
    host="104.156.246.237",
    port=5432,
    dbname="datawarehouse_bi",
    user="sa",
    password="IngDatos123*",
)

cur = conn.cursor()

print("=" * 80)
print("DIM_PROMOCION SCHEMA:")
print("=" * 80)
cur.execute(
    """
    SELECT column_name, data_type, character_maximum_length
    FROM information_schema.columns 
    WHERE table_name = 'dim_promocion' 
    ORDER BY ordinal_position
"""
)
for row in cur.fetchall():
    print(f"  {row}")

print("\n" + "=" * 80)
print("DIM_PROMOCION DATA:")
print("=" * 80)
cur.execute("SELECT * FROM dim_promocion LIMIT 5")
for row in cur.fetchall():
    print(f"  {row}")

cur.close()
conn.close()
