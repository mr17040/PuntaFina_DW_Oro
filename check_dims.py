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
print("DIM_IMPUESTOS:")
print("=" * 80)
cur.execute("SELECT * FROM dim_impuestos ORDER BY impuesto_id")
for row in cur.fetchall():
    print(f"  {row}")

print("\n" + "=" * 80)
print("DIM_PROMOCION:")
print("=" * 80)
cur.execute("SELECT * FROM dim_promocion ORDER BY sk_promocion")
for row in cur.fetchall():
    print(f"  {row}")

cur.close()
conn.close()
