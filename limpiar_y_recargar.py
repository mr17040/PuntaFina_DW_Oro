#!/usr/bin/env python3
"""Limpiar y recargar dimensiones afectadas"""

import psycopg2

conn = psycopg2.connect(
    host="104.156.246.237",
    port=5432,
    database="datawarehouse_bi",
    user="sa",
    password="IngDatos123*",
)

cur = conn.cursor()

print("\n" + "=" * 70)
print("LIMPIANDO DIMENSIONES AFECTADAS")
print("=" * 70)

# 1. TRUNCAR dim_impuestos
print("\n🗑️  Truncando dim_impuestos...")
cur.execute("TRUNCATE TABLE dim_impuestos CASCADE")
conn.commit()
print("   ✓ dim_impuestos truncada")

# 2. TRUNCAR dim_promocion
print("\n🗑️  Truncando dim_promocion...")
cur.execute("TRUNCATE TABLE dim_promocion CASCADE")
conn.commit()
print("   ✓ dim_promocion truncada")

# 3. TRUNCAR fact_ventas para poder recargarla con nuevas FKs
print("\n🗑️  Truncando fact_ventas...")
cur.execute("TRUNCATE TABLE fact_ventas CASCADE")
conn.commit()
print("   ✓ fact_ventas truncada")

print("\n" + "=" * 70)
print("✅ TABLAS LIMPIADAS - LISTAS PARA RECARGA")
print("=" * 70)

cur.close()
conn.close()
